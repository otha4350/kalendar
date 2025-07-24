use axum::{Router, routing::get};
use fantoccini::{ClientBuilder};
use std::fs::File;
use std::io::Write;
use axum::routing::get_service;
use tower_http::services::ServeDir;
mod form;

// get_calendar ics from link
use axum::response::IntoResponse;
use axum::http::StatusCode;

async fn get_calendar(url: &str) -> impl IntoResponse {
    match reqwest::get(url).await {
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
}


#[tokio::main]
async fn main() {
    let otto_url = "";
    let holiday_url = "https://calendar.google.com/calendar/ical/sv.swedish%23holiday%40group.v.calendar.google.com/public/basic.ics";
    // Serve static files from ./src and ICS from /
    let app = Router::new()
        .route("/calendar.ics", get(||get_calendar(otto_url)))
        .route("/holiday.ics", get(||get_calendar(holiday_url)))
        .fallback_service(get_service(ServeDir::new("src")));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001").await.unwrap();

    // Start the server in a background task
    let server = axum::serve(listener, app);
    // Spawn the server in a background task
    tokio::spawn(async move {
            _take_screenshot().await.unwrap_or_else(|e| {
                eprintln!("Screenshot error: {}", e);
            });
        }
    );
    server.await.unwrap();

    // _take_screenshot().await.unwrap();

}

async fn _take_screenshot() -> Result<(), fantoccini::error::CmdError> {
    //connect to geckodriver
    let c = ClientBuilder::native().connect("http://localhost:4444").await.expect("failed to connect to WebDriver");
    c.set_window_size(800+(800-784),480+(480-386)).await?;

    c.goto("localhost:3001").await?;
    tokio::time::sleep(std::time::Duration::from_secs(2)).await; // wait for the page to load

    let bytes = c.screenshot().await?;
        
    let mut file = File::create("screenshot.png")?;
    file.write_all(&bytes)?;
    

    c.close().await
}
