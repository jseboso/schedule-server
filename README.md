# Schedule Server

A personal website featuring my weekly schedule, information about me, and various interactive features.

## Description

Schedule Server is a personal web application built with vanilla HTML, CSS, JavaScript, and Python. It features a custom HTTP server implementation that handles various routes and serves dynamic content. The website showcases my weekly schedule, displays maps of locations, and provides various interactive features including form submissions, stock data retrieval, and search functionality.

## Features

### My Schedule
- Interactive weekly schedule displaying classes, work, and other activities
- Hoverable elements that display relevant images
- Google Maps integration showing location pins in Minneapolis
- Navigation features to calculate walking, driving, or transit distances

### About Me
- Personal information and fun facts
- Photo gallery
- Embedded favorite videos

### Form Input
- Form for entering new events into the calendar
- Fields for location, time, date, URL, and more
- Data validation for proper formatting

### Submission History
- View of all previously submitted events
- Organized in a clean table format

### My Stock
- Stock information retrieval via API
- Real-time stock data display
- Search functionality for different stock symbols

### My Server
- Search functionality for Google and YouTube
- Basic calculator with arithmetic operations
- File explorer to browse server files

## Technical Details

### Server Implementation
- Custom HTTP server built with Python's `http.server` module
- RESTful route handling for different content types
- MIME type detection for proper content serving
- Binary and text file handling

### Front-End Features
- Vanilla JavaScript for dynamic content
- Event listeners for interactive elements
- Google Maps API integration with custom markers
- Form submission and validation

### File Structure
```
.
├── files/                # User accessible files
├── static/
│   ├── audio/            # Audio files
│   ├── css/              # Stylesheet files
│   ├── html/             # HTML pages
│   ├── img/              # Image resources
│   ├── js/               # JavaScript files
│   └── txt/              # Text resources
├── response.log          # Server access logs
├── README.md             # This file
└── server.py             # Main server implementation
```

## Getting Started

### Prerequisites
- Python 3.6 or higher
- Web browser (Chrome, Firefox, Safari, etc.)
- Internet connection for Google Maps and stock API functionality

### Installation
1. Clone the repository
   ```
   git clone https://github.com/yourusername/schedule-server.git
   ```
2. Navigate to the project directory
   ```
   cd schedule-server
   ```
3. Start the server
   ```
   python server.py
   ```
4. Open your browser and navigate to
   ```
   http://localhost:8045/
   ```

## Implementation Details

The server uses a custom request handler that processes different file types and routes:

- HTML files are served from the `static/html/` directory
- Special routes like `EventLog.html` and `SubmissionHistory.html` generate dynamic content
- The `redirect` endpoint handles search queries to Google and YouTube
- The `calculator` endpoint performs basic arithmetic operations
- The file explorer provides access to files in the `files/` directory

The application employs client-side JavaScript for interactive features like image hovering, form validation, and Google Maps integration.

## Future Improvements
- Add user authentication for personalized content
- Implement persistent storage for schedule items
- Enhance mobile responsiveness
- Add more interactive features and visualizations

## Author
Sebas Osorio

## Acknowledgments
- Google Maps JavaScript API
- Stock data API providers
- University of Minnesota for location inspiration