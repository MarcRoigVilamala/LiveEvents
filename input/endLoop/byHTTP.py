from http.server import BaseHTTPRequestHandler, HTTPServer


def create_http_reciever(video_input, server_class=HTTPServer, port=8080):
    class EndLoopHTTPReceiver(BaseHTTPRequestHandler):
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

    server_address = ('192.168.8.229', port)
    httpd = server_class(server_address, EndLoopHTTPReceiver)

    httpd.serve_forever()
