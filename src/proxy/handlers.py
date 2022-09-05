import re
from socketserver import StreamRequestHandler
from typing import NamedTuple

import requests
from requests import Response
from requests.structures import CaseInsensitiveDict

from configuration.settings import settings


class UserRequest(NamedTuple):
    method: str
    url: str
    http_version: str
    headers: dict


class ResponseHandler:
    """
    The class responsible for sending requests to the remote server and
    handling them.
    """

    def get_response_from_remote_server(self, user_request: str) -> tuple[str, bytes]:
        """
        Sends a request to the remote server and returns response headers and
        the response content.
        """
        server_response = self.send_request_to_remote_server(user_request)
        headers_text = self.get_response_headers_text(server_response.headers)
        status_line_with_headers = self.add_status_line_to_headers(
            server_response.status_code, server_response.reason, headers_text
        )
        return status_line_with_headers, server_response.content

    def send_request_to_remote_server(self, requested_url) -> Response:
        """Sends the request to the remote server and returns the response."""
        return requests.get(self.construct_remote_server_url(requested_url))

    @staticmethod
    def get_response_headers_text(headers: CaseInsensitiveDict) -> str:
        """Constructs a headers text from the `headers` dict."""
        headers_text = ""
        for header, value in headers.items():
            header_with_value = f"{header}: {value}\r\n"
            headers_text += header_with_value
        return headers_text

    @staticmethod
    def add_status_line_to_headers(
            status_code: int, status_detail: str, headers_text: str, http_version: str = '1.1'
    ) -> str:
        """
        Adds the status line (Http version + status code + status detail) to
        the headers text and returns the result.
        """
        status_line = f"HTTP/{http_version} {status_code} {status_detail} \r\n"
        return status_line + headers_text

    @staticmethod
    def add_content_to_headers(headers_text: str, content: str) -> str:
        """
        Adds a response content to the headers and returns the result.
        """
        return f"{headers_text}\r\n{content}".strip()

    @staticmethod
    def construct_remote_server_url(asked_url: str):
        """
        Constructs the url using the `self.remote_server_url` and
        the `asked_url`.
        """
        return settings['PROXY_SERVER']['REQUESTED_URL'] + asked_url


class RequestHandler:
    """
    The class responsible for parsing and providing user's request
    in the appropriate form.
    """

    def parse_user_request(self, request_text: str) -> UserRequest:
        """
        Parses a plain request text and returns appropriate
        information about it.
        """
        method, url, http_version, headers = request_text.split(maxsplit=3)
        return UserRequest(
            method=method,
            url=url,
            http_version=http_version,
            headers=self.parse_headers_text(headers)
        )

    @staticmethod
    def parse_headers_text(headers: str) -> dict:
        """Parses plain headers text and returns a dict of them."""
        headers_lines = headers.strip().split('\n')
        headers_dict = {}
        for header_line in headers_lines:
            header, value = header_line.strip().split(": ")
            headers_dict[header] = value
        return headers_dict

    @staticmethod
    def change_host_in_user_request(user_request: str) -> str:
        """Changes the proxy address to the requested server url."""
        proxy_settings = settings['PROXY_SERVER']
        host_with_port_pattern = f"{proxy_settings['HOST']}:{proxy_settings['PORT']}"
        return re.sub(host_with_port_pattern, proxy_settings['REQUESTED_URL'], user_request)


class ProxyHandler(StreamRequestHandler, ResponseHandler, RequestHandler):
    """
    The class responsible for handling requests from the client to the
    remote server and for processing server's responses and sending them
    back to the user.
    """

    def handle(self):
        """
        Accepts a request from the client and returns a server response
        to him.
        """
        user_request = self.get_user_request()

    def get_user_request(self) -> UserRequest:
        """Returns user's request."""
        request_as_plain_text = self.get_plain_text_of_user_request()
        request_with_changed_host = self.change_host_in_user_request(request_as_plain_text)
        return self.parse_user_request(request_with_changed_host)

    def get_plain_text_of_user_request(self) -> str:
        """Returns user's request as a plain text."""
        user_request = b''
        with self.rfile as user_request_in_bytes:
            for line in user_request_in_bytes:
                user_request += line
                if line == b'\r\n' or line == b'\n':
                    break
        return user_request.decode()
