#!/usr/bin/env python3
"""
Personal Website Server
Author: Sebas Osorio
"""

# Add this near the top of your server.py file
from env_config import setup_environment

# Load environment variables at the start of your program
config = setup_environment()

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote_plus, parse_qs
import os
import stat
import sys
from datetime import datetime
import glob
import logging
from typing import Tuple, Dict, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='server.log'
)
logger = logging.getLogger('personal_website')

# Type aliases for better readability
MimeType = str
Response = str

# Configuration dictionaries
MIME_TYPES = {
    "html": "text/html",
    "css": "text/css",
    "js": "application/javascript",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "mp3": "audio/mpeg",
    "txt": "text/plain",
}

CONTENT_FOLDERS = {
    "html": "html",
    "css": "css",
    "js": "js",
    "png": "img",
    "jpg": "img",
    "jpeg": "img",
    "mp3": "audio",
    "txt": "text",
}

# File types that should be read in binary mode
BINARY_TYPES = {"png", "jpg", "jpeg", "mp3"}

# Global storage for events (consider moving this to a database in the future)
all_events = ""

def parse_form_data(body: Optional[str]) -> Dict[str, str]:
    """Parse form data from request body.
    
    Args:
        body: The request body string
        
    Returns:
        Dictionary with parsed parameters
    """
    if not body:
        return {}
        
    parameters = body.split("&")
    
    # Split each parameter into a (key, value) pair, and escape both
    def split_parameter(parameter: str) -> Tuple[str, str]:
        k, v = parameter.split("=", 1)
        return unquote_plus(k), unquote_plus(v)
    
    body_dict = dict(map(split_parameter, parameters))
    logger.info(f"Parsed parameters: {body_dict}")
    return body_dict

def add_event_to_table(event_data: Dict[str, str]) -> str:
    """Format an event as an HTML table row and add to global event history.
    
    Args:
        event_data: Dictionary containing event details
        
    Returns:
        HTML string for the table row
    """
    event_html = f"""
        <tr>
            <td>{event_data.get("eventname", "")}</td>
            <td>{event_data.get("dayofweek", "")}</td>
            <td>{event_data.get("starttime", "")}</td>
            <td>{event_data.get("endtime", "")}</td>
            <td>{event_data.get("phonenumber", "")}</td>
            <td>{event_data.get("location", "")}</td>
            <td>{event_data.get("extrainfo", "")}</td>
            <td>{event_data.get("url", "")}</td>
        </tr>
    """
    global all_events
    all_events += event_html
    return event_html

def log_response(request: str, response: Any) -> None:
    """Log the request and response to a file."""
    log_file_path = config['LOG_FILE']
    with open(log_file_path, 'a') as log_file:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        log_line = f"{current_time}, {request}, {response}\n"
        log_file.write(log_line)

def has_read_permission(file_path: str) -> bool:
    """Check if a file has read permissions.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file has read permissions, False otherwise
    """
    stmode = os.stat(file_path).st_mode
    return (getattr(stat, 'S_IROTH') & stmode) > 0

def handle_request(url: str, body: Optional[str] = None) -> Tuple[str, MimeType]:
    """Process HTTP requests and return appropriate responses.
    
    Args:
        url: The request URL
        body: Optional request body for POST requests
        
    Returns:
        Tuple containing (response content, MIME type)
    """
    # Parse URL and split off query parameters
    url_parts = url.split("?", 1)
    url_path = url_parts[0]
    query_string = url_parts[1] if len(url_parts) > 1 else None
    
    # Parse form parameters for POST requests
    parameters = parse_form_data(body) if body else {}
    
    # Extract file information
    basename = os.path.basename(url_path)
    root, extension = os.path.splitext(basename)
    extension = extension[1:] if extension else ""
    
    logger.debug(f"Requested file: {basename}, extension: {extension}")
    
    # Determine content type and MIME type
    try:
        folder = CONTENT_FOLDERS.get(extension, "text")
        mime = MIME_TYPES.get(extension, "text/plain")
    except:
        folder = "text"
        mime = "text/plain"
    
    # Handle binary files
    if extension in BINARY_TYPES:
        try:
            with open(f"static/{folder}/{basename}", "rb") as f:
                return f.read(), mime
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Error accessing file: {e}")
            return handle_error(e)
    
    # Handle special routes
    if basename == "EventLog.html":
        return generate_event_log(parameters)
    elif basename == "SubmissionHistory.html":
        return generate_submission_history()
    elif basename == "redirect":
        redirect_url = build_redirect_url(query_string)
        return redirect_url, "redirect"
    elif basename == "calculator":
        result = calculate(query_string)
        return str(result), "calculator"
    elif basename == "explorer.html":
        return generate_file_explorer(), "text/html"
    elif basename == "stockQuotes.html":
        return serve_stock_quotes_page()
    elif basename == "MySchedule.html":
        return serve_schedule_page()
    
    # Handle regular files
    try:
        with open(f"static/{folder}/{basename}", "r") as f:
            return f.read(), mime
    except FileNotFoundError:
        logger.error(f"File not found: {basename}")
        with open("static/html/404.html", "r") as f:
            return f.read(), "text/html"
    except PermissionError:
        logger.error(f"Permission denied: {basename}")
        with open("static/html/403.html", "r") as f:
            return f.read(), "text/html"
        
def serve_schedule_page() -> Tuple[str, MimeType]:
    """Serve the schedule page with injected Google Maps API key from environment variables."""
    try:
        # Get the API key from environment variables
        maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', 'AIzaSyAzT6-ldxhAWi5ZIKm20YtkVGobVCfbvmE')  # Use existing key as fallback
        
        # Read the schedule template
        with open("static/html/MySchedule.html", "r") as f:
            content = f.read()
        
        # Replace the placeholder with the actual API key
        content = content.replace('{{GOOGLE_MAPS_API_KEY}}', maps_api_key)
        
        # Return the modified content
        return content, "text/html"
    except Exception as e:
        logger.error(f"Error serving schedule page: {e}")
        return f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>", "text/html"

def serve_stock_quotes_page() -> Tuple[str, MimeType]:
    """Serve the stock quotes page with injected API key from environment variables."""
    try:
        # Get the API key from environment variables
        stock_api_key = os.environ.get('STOCK_API_KEY', 'SVWB0SITAYWCPOYL')  # Use existing key as fallback
        
        # Read the stock quotes template
        with open("static/html/stockQuotes.html", "r") as f:
            content = f.read()
        
        # Replace the placeholder with the actual API key
        content = content.replace('{{STOCK_API_KEY}}', stock_api_key)
        
        # Return the modified content
        return content, "text/html"
    except Exception as e:
        logger.error(f"Error serving stock quotes page: {e}")
        return f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>", "text/html"

def handle_error(error):
    """Handle file access errors.
    
    Args:
        error: The exception that occurred
        
    Returns:
        Tuple with error page and MIME type
    """
    if isinstance(error, FileNotFoundError):
        with open("static/html/404.html", "r") as f:
            return f.read(), "text/html"
    elif isinstance(error, PermissionError):
        with open("static/html/403.html", "r") as f:
            return f.read(), "text/html"
    else:
        return f"<html><body><h1>Server Error</h1><p>{str(error)}</p></body></html>", "text/html"

def generate_event_log(parameters: Dict[str, str]) -> Tuple[str, MimeType]:
    """Generate HTML for the event log page.
    
    Args:
        parameters: Event data from form submission
        
    Returns:
        Tuple with HTML content and MIME type
    """
    return (
        """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Event Submission</title>
                <link rel="stylesheet" href="../css/stylesheet.css">
            </head>
            <body>
                <header>
                  <nav>
                    <ul>
                        <li><a href="./MySchedule.html">My Schedule</a></li>
                        <li><a href="./AboutMe.html">About Me</a></li>
                        <li><a href="./MyForm.html">Form Input</a></li>
                        <li><a href="./SubmissionHistory.html">Submission History</a></li>
                        <li><a href="./stockQuotes.html">My Stock</a></li>
                        <li><a href="./MyServer.html">My Server</a></li>
                    </ul>
                </nav>
                </header>
                <div>
                    <h1 class="banner"> My New Events</h1>
                </div>
                <div>
                    <table class="clock-table">
                        <thead>
                            <tr>
                                <th>Event</th>
                                <th>Day</th>
                                <th>Start</th>
                                <th>End</th>
                                <th>Phone</th>
                                <th>Location</th>
                                <th>Extra Info</th>
                                <th>URL</th>
                            </tr>
                        </thead>
                        <tbody>
                        """
        + add_event_to_table(parameters)
        + """
                        </tbody>
                    </table>
                </div>
            </body>
            </html>""",
        "text/html; charset=utf-8",
    )

def generate_submission_history() -> Tuple[str, MimeType]:
    """Generate HTML for the submission history page.
    
    Returns:
        Tuple with HTML content and MIME type
    """
    return (
        """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Event Submission</title>
                <link rel="stylesheet" href="../css/stylesheet.css">
            </head>
            <body>
                <header>
                  <nav>
                    <ul>
                        <li><a href="./MySchedule.html">My Schedule</a></li>
                        <li><a href="./AboutMe.html">About Me</a></li>
                        <li><a href="./MyForm.html">Form Input</a></li>
                        <li><a class="current-page" href="./SubmissionHistory.html">Submission History</a></li>
                        <li><a href="./stockQuotes.html">My Stock</a></li>
                        <li><a href="./MyServer.html">My Server</a></li>
                    </ul>
                </nav>
                </header>
                <div>
                    <h1 class="banner"> Form Submission History</h1>
                </div>
                <div>
                    <table class="clock-table">
                        <thead>
                            <tr>
                                <th>Event</th>
                                <th>Day</th>
                                <th>Start</th>
                                <th>End</th>
                                <th>Phone</th>
                                <th>Location</th>
                                <th>Extra Info</th>
                                <th>URL</th>
                            </tr>
                        </thead>
                        <tbody>
                        """
        + all_events
        + """
                        </tbody>
                    </table>
                </div>
            </body>
            </html>""",
        "text/html; charset=utf-8",
    )

def build_redirect_url(query_string: Optional[str]) -> str:
    """Build a redirect URL based on search parameters.
    
    Args:
        query_string: Query string from the URL
        
    Returns:
        Redirect URL
    """
    if not query_string:
        return "https://www.google.com"
        
    parsed_query = parse_qs(query_string)
    
    search_term = parsed_query.get('searchterm', [''])[0]
    search_source = parsed_query.get('searchsource', ['google'])[0]
    
    url_string = f"https://www.{search_source}.com/"
    
    if search_source == "google":
        url_string += f"search?q={search_term}"
    elif search_source == "youtube":
        url_string += f"results?search_query={search_term}"
    
    return url_string

def calculate(query_string: Optional[str]) -> float:
    """Calculate a simple arithmetic expression.
    
    Args:
        query_string: Query string from the URL
        
    Returns:
        Result of the calculation
    """
    if not query_string:
        return 0
        
    parsed_query = parse_qs(query_string)
    
    try:
        digit1 = int(parsed_query.get('digit1', ['0'])[0])
        operator = parsed_query.get('operator', ['plus'])[0]
        digit2 = int(parsed_query.get('digit2', ['0'])[0])
        
        if operator == "plus":
            return digit1 + digit2
        elif operator == "minus":
            return digit1 - digit2
        elif operator == "multiply":
            return digit1 * digit2
        elif operator == "divide":
            # Avoid division by zero
            if digit2 == 0:
                return "Error: Division by zero"
            return digit1 / digit2
        else:
            return f"Error: Unknown operator '{operator}'"
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        return f"Error: {str(e)}"

def generate_file_explorer() -> str:
    """Generate HTML for the file explorer page.
    
    Returns:
        HTML content
    """
    replace_element = """<tbody id="replace-files">
                <tr>
                    <td>No files found</td>
                </tr>
            </tbody>"""
            
    file_rows = []
    for file_path in glob.glob("./files/*"):
        file_name = os.path.basename(file_path)
        file_extension = file_name.split(".")[-1] if "." in file_name else ""
        
        if file_extension in MIME_TYPES:
            file_rows.append(f'<tr><td><a href="{file_path}">{file_name}</a></td></tr>')
    
    new_table = "".join(file_rows) if file_rows else replace_element
    
    try:
        with open("./static/html/explorer.html", "r") as f:
            files_page = f.read()
            files_page = files_page.replace(replace_element, new_table)
            return files_page
    except Exception as e:
        logger.error(f"Error generating file explorer: {e}")
        return f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"

class RequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler for the personal website."""
    
    def _read_body(self) -> str:
        """Read and parse the request body.
        
        Returns:
            Request body as a string
        """
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        return str(body, encoding="utf-8")

    def _send_response(self, message, response_code, headers):
        """Send HTTP response with headers.
        
        Args:
            message: Response content
            response_code: HTTP status code
            headers: Dictionary of HTTP headers
        """
        # Convert string message to bytes if needed
        if isinstance(message, str):
            message = bytes(message, "utf8")

        # Send response code
        self.protocol_version = "HTTP/1.1"
        self.send_response(response_code)

        # Send all headers
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(message)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        # Send the response body
        self.wfile.write(message)

    def do_GET(self):
        """Handle GET requests."""
        logger.info(f"GET request: {self.path}")
        
        # Process the request
        message, content_type = handle_request(self.path)
        
        # Handle special case for redirects
        if content_type == "redirect":
            redirect_url = message
            self._send_response(
                bytes("Redirecting...", "utf8"),
                307,
                {
                    "Location": redirect_url,
                },
            )
            
            log_res = [
                307,
                {
                    "Location": redirect_url,
                },
            ]
            log_response(str(self.path) + " ", log_res)
            return
            
        # Handle calculator responses or other text responses
        if isinstance(message, str):
            message = bytes(message, "utf8")
            
        # Send normal response
        self._send_response(
            message,
            200,
            {
                "Content-Type": content_type,
            },
        )
        
        # Log the response
        log_res = [
            200,
            {
                "Content-Type": content_type,
                "Content-Length": len(message),
                "X-Content-Type-Options": "nosniff",
            }
        ]
        log_response(str(self.path) + " ", log_res)

    def do_POST(self):
        """Handle POST requests."""
        logger.info(f"POST request: {self.path}")
        
        # Read the request body
        body = self._read_body()
        
        # Process the request
        message, content_type = handle_request(self.path, body)

        # Convert string to bytes if needed
        if isinstance(message, str):
            message = bytes(message, "utf8")

        # Send the response
        self._send_response(
            message,
            200,
            {
                "Content-Type": content_type,
            },
        )
        
        # Log the response
        log_res = [
            200,
            {
                "Content-Type": content_type,
                "Content-Length": len(message),
                "X-Content-Type-Options": "nosniff",
            }
        ]
        log_response(str(self.path) + " " + str(body), log_res)

def main():
    """Start the web server."""
    PORT = config['PORT']
    HOST = config['HOST']
    server_address = (HOST, PORT)
    
    print(f"Starting server at http://{HOST}:{PORT}/")
    print(f"Press Ctrl+C to stop the server")
    
    try:
        httpd = HTTPServer(server_address, RequestHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
        print("Server stopped successfully")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()