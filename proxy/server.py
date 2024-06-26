from http.server import SimpleHTTPRequestHandler, HTTPServer
import requests
from bs4 import BeautifulSoup


class ProxyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        target_url = self.path

        response = requests.get(target_url)
        content = self.remove_ads(response.text)

        self.send_response(response.status_code)
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def remove_ads(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for ad in soup.find_all(class_='ad'):
            ad.decompose()
        return str(soup)


def run(server_class=HTTPServer, handler_class=ProxyHTTPRequestHandler,
        port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting proxy server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
