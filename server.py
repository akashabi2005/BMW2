import http.server
import socketserver
import sqlite3
import urllib.parse
import os

PORT = 8000
DB_FILE = "bookings.db"

# Initialize SQLite DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            date TEXT NOT NULL,
            model TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/book':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            
            # Extract fields
            name = parsed_data.get('name', [''])[0]
            email = parsed_data.get('email', [''])[0]
            date = parsed_data.get('date', [''])[0]
            model = parsed_data.get('model', [''])[0]
            
            # Insert into database
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("INSERT INTO bookings (name, email, date, model) VALUES (?, ?, ?, ?)",
                          (name, email, date, model))
                conn.commit()
                conn.close()
                
                # Send success response & redirect back
                self.send_response(303)
                self.send_header('Location', '/?success=1#book')
                self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

# This allows us to serve the index.html directly from root and cleanly resolve
# any specific requests including videos if needed. Built-in SimpleHTTPRequestHandler 
# does this already, we just augmented it with POST for /book

if __name__ == "__main__":
    init_db()
    
    Handler = CustomHandler
    
    class TCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    with TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print("Server stopped.")
