import http.server
import socketserver
import json
import gzip
import io

# Can change the port to desired port which is not conflicting with any other service on the server
PORT = 7000

def get_blocked_domains():
    # Reads and returns the list of blocked domains from the 'dns.blacklist' file
    with open("dns.blacklist", "r") as f:
        blocked_domains = f.read().splitlines()
    return blocked_domains

class HTTPServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/v1/API.json":
            # Fetches the list of blocked domains
            blocked_domains = get_blocked_domains()
            response_data = json.dumps(blocked_domains).encode('utf-8')

            # Compresses the data using gzip for efficient transfer
            compressed_data = io.BytesIO()
            with gzip.GzipFile(fileobj=compressed_data, mode='wb') as f:
                f.write(response_data)
            compressed_data.seek(0)

            # Sends the compressed data as the response
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(compressed_data.getvalue())))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(compressed_data.read())
        else:
            # Handles other GET requests as per default behavior
            super().do_GET()

with socketserver.TCPServer(("", PORT), HTTPServerHandler) as httpd:
    # Starts the HTTP server to serve the blocked domains as JSON data
    print(f"Serving JSON data at http://127.0.0.1:{PORT}/v1/API.json")
    httpd.serve_forever()
