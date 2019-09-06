from http.server import BaseHTTPRequestHandler, HTTPServer


def create_http_reciever(video_input, server_class=HTTPServer, port=8080):
    class MyHTTPReceiver(BaseHTTPRequestHandler):
        def _set_headers(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            video_input.stop_loop()
            self._set_headers()

        def do_POST(self):
            video_input.stop_loop()
            self._set_headers()

    server_address = ('', port)
    httpd = server_class(server_address, MyHTTPReceiver)

    httpd.serve_forever()
