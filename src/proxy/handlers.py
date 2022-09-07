import re
from socketserver import StreamRequestHandler
from typing import NamedTuple, Mapping

import requests
from requests import Response
from requests.structures import CaseInsensitiveDict

from configuration.settings import settings, ProxyServerSettings


class UserRequest(NamedTuple):
    method: str
    url: str
    http_version: str
    headers: dict


class HttpParser:

    @property
    def proxy_settings(self) -> ProxyServerSettings:
        """Returns a proxy settings."""
        return settings['PROXY_SERVER']

    def construct_remote_server_url(self, asked_url: str):
        """Constructs the remote server url for sending requests to it."""
        return self.proxy_settings['REQUESTED_URL'] + asked_url

    @staticmethod
    def construct_http_response(
            status_line: str, headers: str, content: bytes
    ) -> bytes:
        """Constructs a http response."""
        http_response_units = [status_line.encode(), headers.encode(), content]
        return b'\r\n'.join(http_response_units)

    @staticmethod
    def get_status_line(
            status_code: int, reason: str, http_version: str = '1.1'
    ) -> str:
        """Constructs the status line (Http version + status code + status detail)."""
        status_line = f"HTTP/{http_version} {status_code} {reason}"
        return status_line

    @staticmethod
    def get_headers_text(headers: Mapping) -> str:
        """
        Construct headers text from mapping of headers and their
        values.
        """
        headers_text = ""
        for header, value in headers.items():
            headers_text += f"{header}: {value}\r\n"
        return headers_text

    @staticmethod
    def get_headers_dict(headers: str) -> dict:
        """Parses plain headers text and returns a dict of them."""
        headers_lines = headers.strip().split('\n')
        headers_dict = {}
        for header_line in headers_lines:
            header, value = header_line.strip().split(": ")
            headers_dict[header] = value
        return headers_dict


class ResponseHandler(HttpParser):
    """
    The class responsible for sending requests to the remote server and
    handling them.
    """

    def get_response_from_remote_server(self, user_request: UserRequest) -> bytes:
        """
        Sends a request to the remote server and returns response headers
        and the response content.
        """
        server_response_data = self.send_user_request_to_server(user_request)
        status_line, headers, content = self.get_server_response_parts(server_response_data)
        return self.construct_http_response(status_line, headers, content)

    def send_user_request_to_server(self, user_request: UserRequest) -> Response:
        """Sends the client request to the remote server with changed url."""
        server_response_data = requests.request(
            user_request.method,
            self.construct_remote_server_url(user_request.url),
            headers=user_request.headers,
        )
        return server_response_data

    def get_server_response_parts(self, server_response_data: Response) -> tuple[str, str, bytes]:
        status_line = self.get_status_line(
            server_response_data.status_code, server_response_data.reason
        )
        content = self.modify_response_content(
            server_response_data.content, server_response_data.headers
        )
        modified_headers = self.modify_response_headers(
            content, server_response_data.headers
        )
        headers_as_text = self.get_headers_text(modified_headers)
        return status_line, headers_as_text, content

    @staticmethod
    def modify_response_content(content: bytes, headers: CaseInsensitiveDict) -> bytes:
        """
        Modifies a content of the response if it is type of `text/html`. Otherwise,
        returns how it was passed.
        """
        content_type_of_response = headers.get("Content-Type")
        if content_type_of_response and 'text/html' in content_type_of_response:
            pass
        return content

    @staticmethod
    def modify_response_headers(content: bytes, headers: CaseInsensitiveDict) -> CaseInsensitiveDict:
        """
        Modifies headers. Set a `Content-Length` header and removes a chunk
        encoding if it was provided.
        """
        headers.pop('Transfer-Encoding', False)
        headers.pop('Content-Encoding', False)
        headers.update({'Content-Length': len(content)})
        return headers


class RequestHandler(HttpParser):
    """
    The class responsible for parsing and providing user's request
    in the appropriate form.
    """

    def parse_raw_http_text(self, request_text: bytes | str) -> UserRequest:
        """
        Parses a plain request text and returns appropriate
        information about it.
        """
        method, url, http_version, headers = request_text.split(maxsplit=3)
        return UserRequest(
            method=method,
            url=url,
            http_version=http_version,
            headers=self.get_headers_dict(headers)
        )

    def change_host_in_user_request(self, user_request: str) -> str:
        """Changes the proxy address to the requested server url."""
        remote_server_host = self._get_host_from_remote_server_url()
        host_with_port_pattern = f"{self.proxy_settings['HOST']}:{self.proxy_settings['PORT']}"
        return re.sub(host_with_port_pattern, remote_server_host, user_request)

    def _get_host_from_remote_server_url(self):
        """
        Returns host from the remote server url or raises Error if url is invalid.
        """
        if not (remote_server_host := re.search(r"(?<=://).*", self.proxy_settings['REQUESTED_URL'])):
            raise ValueError("`REQUESTED_URL` in the configuration file has invalid value.")
        return remote_server_host.group()


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
        server_response = self.get_response_from_remote_server(user_request)
        status_line, headers, content = self.get_server_response_parts(
            self.send_user_request_to_server(user_request)
        )
        self.send_response_to_user(self.construct_http_response(status_line, headers, content))

    def get_user_request(self) -> UserRequest:
        """Returns user's request."""
        request_as_plain_text = self.get_plain_text_of_user_request()
        request_with_changed_host = self.change_host_in_user_request(request_as_plain_text)
        return self.parse_raw_http_text(request_with_changed_host)

    def get_plain_text_of_user_request(self) -> str:
        """Returns user's request as a plain text."""
        user_request = b''
        with self.rfile as user_request_in_bytes:
            for line in user_request_in_bytes:
                user_request += line
                if line == b'\r\n' or line == b'\n':
                    break
        return user_request.decode()

    def send_response_to_user(self, message: bytes):
        self.wfile.write(message)
