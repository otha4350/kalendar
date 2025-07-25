use axum::{
    extract::{Path, State},
    response::{Html, IntoResponse},
    routing::{get},
    Router,
    http::StatusCode,
};
use axum::routing::get_service;
use tower_http::services::ServeDir;

mod form;

use form::{CalendarStore, calendar_routes};

// Updated get_calendar function to work with calendar store
async fn get_calendar_by_id(
    State(store): State<CalendarStore>,
    Path(id): Path<String>
) -> impl IntoResponse {
    match store.get(&id) {
        Some(calendar) => {
            match reqwest::get(&calendar.ics_url).await {
                Ok(resp) => match resp.text().await {
                    Ok(text) => (
                        StatusCode::OK,
                        [
                            ("Content-Type", "text/calendar; charset=utf-8"),
                            ("Access-Control-Allow-Origin", "*")
                        ],
                        text
                    ).into_response(),
                    Err(_) => (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        "Failed to read response text"
                    ).into_response(),
                },
                Err(_) => (
                    StatusCode::BAD_GATEWAY,
                    "Failed to fetch calendar"
                ).into_response(),
            }
        },
        None => (
            StatusCode::NOT_FOUND,
            "Calendar not found"
        ).into_response(),
    }
}

// Main calendar page that displays all enabled calendars
async fn calendar_page(State(store): State<CalendarStore>) -> Html<String> {
    let enabled_calendars = store.get_enabled();
    
    // Generate fullcalendar eventSources from enabled calendars
    let event_sources = enabled_calendars
        .iter()
        .map(|cal| {
            format!(
                r#"{{
                    url: '/ical/{}',
                    format: 'ics',
                    color: '{}'
                }}"#,
                cal.id, cal.color
            )
        })
        .collect::<Vec<_>>()
        .join(",");
    

    let index_str = include_str!("index.html");
    let html_template = index_str.replace("<!--event_sources-->", &event_sources);
    Html(html_template)
}

#[tokio::main]
async fn main() {

    // Initialize the calendar store
    let calendar_store = CalendarStore::new("calendars.csv");
    
    // Pre-populate with your existing calendars if CSV is empty
    let calendars = calendar_store.get_all();
    if calendars.is_empty() {
        println!("No calendars found, adding default calendars...");
        
        // Add your existing calendars
        
        let holiday_calendar = form::Calendar {
            id: String::new(), // Will be auto-generated
            name: "Swedish Holidays".to_string(),
            color: "#d73027".to_string(),
            ics_url: "https://calendar.google.com/calendar/ical/sv.swedish%23holiday%40group.v.calendar.google.com/public/basic.ics".to_string(),
            enabled: true,
        };
        
        
        calendar_store.add(holiday_calendar).unwrap_or_else(|e| {
            eprintln!("Failed to add holiday calendar: {}", e);
        });
        
        println!("Default calendars added successfully!");
    }
    
    // Build the router with all routes
    let app = Router::new()
        .route("/", get(calendar_page))
        .route("/ical/{id}", get(get_calendar_by_id))
        .merge(calendar_routes(calendar_store.clone()))
        .fallback_service(get_service(ServeDir::new("src")))
        .with_state(calendar_store);
    
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001").await.unwrap();
    println!("Server running on http://0.0.0.0:3001");
    println!("Calendar view: http://localhost:3001");
    println!("Calendar management: http://localhost:3001/calendars");
    
    let server = axum::serve(listener, app);
    
    server.await.unwrap();
}