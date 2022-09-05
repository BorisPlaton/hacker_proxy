from socketserver import StreamRequestHandler

import requests
from requests.structures import CaseInsensitiveDict

from configuration.settings import settings


class ProxyHandler(StreamRequestHandler):
    proxy_settings = settings['PROXY_SERVER']

    def handle(self):
        asked_url = self.get_url_from_http_request()
        requested_url = self.construct_requested_url(asked_url)
        status_line, headers, content = self.request_remote_server(requested_url)
        server_response = self.construct_server_response(status_line, headers, content)
        self.send_to_client_response('hi')

    def send_to_client_response(self, content: str):
        self.wfile.write(content.encode())

    def get_url_from_http_request(self) -> str:
        """Returns the asked url from http request."""
        first_line_of_http_request = self.rfile.readline()
        _, request_url, _ = first_line_of_http_request.split()
        return request_url.decode()

    @classmethod
    def construct_requested_url(cls, asked_url: str):
        """
        Constructs the url using the `REQUESTED_URL` from
        project config.
        """
        return cls.proxy_settings['REQUESTED_URL'] + asked_url

    @staticmethod
    def request_remote_server(requested_url) -> tuple[str, CaseInsensitiveDict, str]:
        response = requests.get(requested_url)
        return f"HTTP/1.1 {response.status_code} {response.reason}", response.headers, response.text

    @staticmethod
    def construct_server_response(status_line: str, headers: CaseInsensitiveDict, content: str) -> str:
        headers_str = '\r\n'.join([f'{header}: {value}' for header, value in headers.items()]) + '\r\n'
        return '\r\n\r\n'.join([status_line + '\r\n' + headers_str, content])
