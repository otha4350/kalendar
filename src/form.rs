use axum::{
    extract::{Form, Path, State},
    http::StatusCode,
    response::{Html, Redirect},
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::sync::{Arc, RwLock};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Calendar {
    pub id: String,
    pub name: String,
    pub color: String,
    pub ics_url: String,
    pub enabled: bool,
}

#[derive(Debug, Clone)]
pub struct CalendarStore {
    calendars: Arc<RwLock<HashMap<String, Calendar>>>,
    csv_path: String,
}

impl CalendarStore {
    pub fn new(csv_path: &str) -> Self {
        let store = CalendarStore {
            calendars: Arc::new(RwLock::new(HashMap::new())),
            csv_path: csv_path.to_string(),
        };
        
        // Load existing calendars from CSV
        if let Err(e) = store.load_from_csv() {
            eprintln!("Failed to load calendars from CSV: {}", e);
        }
        
        store
    }
    
    pub fn load_from_csv(&self) -> Result<(), Box<dyn std::error::Error>> {
        if !std::path::Path::new(&self.csv_path).exists() {
            // Create empty CSV with headers
            fs::write(&self.csv_path, "id,name,color,ics_url,enabled\n")?;
            return Ok(());
        }
        
        let content = fs::read_to_string(&self.csv_path)?;
        let mut reader = csv::Reader::from_reader(content.as_bytes());
        
        let mut calendars = self.calendars.write().unwrap();
        calendars.clear();
        
        for result in reader.deserialize() {
            let calendar: Calendar = result?;
            calendars.insert(calendar.id.clone(), calendar);
        }
        
        Ok(())
    }
    
    pub fn save_to_csv(&self) -> Result<(), Box<dyn std::error::Error>> {
        let calendars = self.calendars.read().unwrap();
        let mut writer = csv::Writer::from_writer(Vec::new());
        
        for calendar in calendars.values() {
            writer.serialize(calendar)?;
        }
        
        let csv_data = String::from_utf8(writer.into_inner()?)?;
        fs::write(&self.csv_path, csv_data)?;
        
        Ok(())
    }
    
    pub fn get_all(&self) -> Vec<Calendar> {
        let calendars = self.calendars.read().unwrap();
        calendars.values().cloned().collect()
    }
    
    pub fn get_enabled(&self) -> Vec<Calendar> {
        let calendars = self.calendars.read().unwrap();
        calendars.values().filter(|c| c.enabled).cloned().collect()
    }
    
    pub fn get(&self, id: &str) -> Option<Calendar> {
        let calendars = self.calendars.read().unwrap();
        calendars.get(id).cloned()
    }
    
    pub fn add(&self, mut calendar: Calendar) -> Result<(), Box<dyn std::error::Error>> {
        if calendar.id.is_empty() {
            calendar.id = Uuid::new_v4().to_string();
        }
        
        let mut calendars = self.calendars.write().unwrap();
        calendars.insert(calendar.id.clone(), calendar);
        drop(calendars);
        
        self.save_to_csv()
    }
    
    pub fn update(&self, id: &str, updated_calendar: Calendar) -> Result<(), Box<dyn std::error::Error>> {
        let mut calendars = self.calendars.write().unwrap();
        if calendars.contains_key(id) {
            calendars.insert(id.to_string(), updated_calendar);
            drop(calendars);
            self.save_to_csv()
        } else {
            Err("Calendar not found".into())
        }
    }
    
    pub fn delete(&self, id: &str) -> Result<(), Box<dyn std::error::Error>> {
        let mut calendars = self.calendars.write().unwrap();
        if calendars.remove(id).is_some() {
            drop(calendars);
            self.save_to_csv()
        } else {
            Err("Calendar not found".into())
        }
    }
    
    pub fn toggle_enabled(&self, id: &str) -> Result<(), Box<dyn std::error::Error>> {
        let mut calendars = self.calendars.write().unwrap();
        if let Some(calendar) = calendars.get_mut(id) {
            calendar.enabled = !calendar.enabled;
            drop(calendars);
            self.save_to_csv()
        } else {
            Err("Calendar not found".into())
        }
    }
}

#[derive(Deserialize)]
pub struct CalendarForm {
    name: String,
    color: String,
    ics_url: String,
    enabled: Option<String>,
}

// Route handlers
pub async fn calendar_management_page(State(store): State<CalendarStore>) -> Html<String> {
    let calendars = store.get_all();
    
    // Read the HTML template
    let html_template = include_str!("calendar_management.html");
    
    let calendar_rows = calendars
        .iter()
        .map(|cal| {
            format!(
                r#"<tr>
                    <td>{}</td>
                    <td><span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></span></td>
                    <td>{}</td>
                    <td style="max-width: 200px; word-break: break-all;">{}</td>
                    <td>{}</td>
                    <td>
                        <button onclick="editCalendar('{}')" class="btn btn-sm">Edit</button>
                        <form style="display: inline;" method="post" action="/calendars/{}/toggle">
                            <button type="submit" class="btn btn-sm {}">{}</button>
                        </form>
                        <form style="display: inline;" method="post" action="/calendars/{}/delete" onsubmit="return confirm('Are you sure?')">
                            <button type="submit" class="btn btn-sm btn-danger">Delete</button>
                        </form>
                    </td>
                </tr>"#,
                cal.name,
                cal.color,
                cal.color,
                cal.ics_url,
                if cal.enabled { "✓" } else { "✗" },
                cal.id,
                cal.id,
                if cal.enabled { "btn-warning" } else { "btn-success" },
                if cal.enabled { "Disable" } else { "Enable" },
                cal.id
            )
        })
        .collect::<Vec<_>>()
        .join("");
    
    // Replace the placeholder in the template
    let html_content = html_template.replace("<!-- Calendar rows will be inserted here -->", &calendar_rows);
    
    Html(html_content)
}

pub async fn add_calendar(
    State(store): State<CalendarStore>,
    Form(form): Form<CalendarForm>,
) -> Result<Redirect, StatusCode> {
    let calendar = Calendar {
        id: String::new(), // Will be generated in add()
        name: form.name,
        color: form.color,
        ics_url: form.ics_url,
        enabled: form.enabled.is_some(),
    };
    
    match store.add(calendar) {
        Ok(_) => Ok(Redirect::to("/calendars")),
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn update_calendar(
    State(store): State<CalendarStore>,
    Path(id): Path<String>,
    Form(form): Form<CalendarForm>,
) -> Result<Redirect, StatusCode> {
    let calendar = Calendar {
        id: id.clone(),
        name: form.name,
        color: form.color,
        ics_url: form.ics_url,
        enabled: form.enabled.is_some(),
    };
    
    match store.update(&id, calendar) {
        Ok(_) => Ok(Redirect::to("/calendars")),
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn get_calendar(
    State(store): State<CalendarStore>,
    Path(id): Path<String>,
) -> Result<Json<Calendar>, StatusCode> {
    match store.get(&id) {
        Some(calendar) => Ok(Json(calendar)),
        None => Err(StatusCode::NOT_FOUND),
    }
}

pub async fn delete_calendar(
    State(store): State<CalendarStore>,
    Path(id): Path<String>,
) -> Result<Redirect, StatusCode> {
    match store.delete(&id) {
        Ok(_) => Ok(Redirect::to("/calendars")),
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn toggle_calendar(
    State(store): State<CalendarStore>,
    Path(id): Path<String>,
) -> Result<Redirect, StatusCode> {
    match store.toggle_enabled(&id) {
        Ok(_) => Ok(Redirect::to("/calendars")),
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn get_enabled_calendars(
    State(store): State<CalendarStore>,
) -> Json<Vec<Calendar>> {
    Json(store.get_enabled())
}

// Add these routes to your existing router
pub fn calendar_routes(store: CalendarStore) -> Router<CalendarStore> {
    Router::new()
        .route("/calendars", get(calendar_management_page))
        .route("/calendars", post(add_calendar))
        .route("/calendars/{id}", post(update_calendar))
        .route("/calendars/{id}", get(get_calendar))
        .route("/calendars/{id}/delete", post(delete_calendar))
        .route("/calendars/{id}/toggle", post(toggle_calendar))
        .route("/api/calendars", get(get_enabled_calendars))
        .with_state(store)
}
