import re
from socketserver import StreamRequestHandler
from typing import NamedTuple, Mapping, BinaryIO

import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.structures import CaseInsensitiveDict

from configuration.settings import settings


class UserRequest(NamedTuple):
    method: str
    url: str
    http_version: str
    headers: dict


class HttpParts(NamedTuple):
    status_line: str
    headers: str
    content: bytes


class HttpParser:
    """The class constructs and parses http request/response."""

    def construct_http_response(
            self, status_line: str, headers: str, content: bytes
    ) -> bytes:
        """Constructs a http response."""
        status_line, headers = map(self.set_http_part_ends_with_crlf, [status_line, headers])
        return status_line.encode() + headers.encode() + b'\r\n' + content

    @staticmethod
    def set_http_part_ends_with_crlf(http_part: str) -> str:
        """
        If the http part has the crlf (\r\n) in the end then returns how it was
        passed. Otherwise, adds the crlf to the end.
        """
        http_part += '' if http_part.endswith('\r\n') else '\r\n'
        return http_part

    @staticmethod
    def get_plain_text_of_user_request(binary_file_of_socket: BinaryIO) -> str:
        """
        Returns the user's request as a plain text from the binary file
        of the socket representation.
        """
        user_request = b''
        with binary_file_of_socket as user_request_in_bytes:
            for line in user_request_in_bytes:
                if not isinstance(line, bytes):
                    raise ValueError("You have to pass BinaryIO to read user request.")
                user_request += line
                if line == b'\r\n':
                    break
        return user_request.decode().strip()

    @staticmethod
    def construct_response_status_line(
            status_code: int | str, reason: str, http_version: str | int | float = '1.1'
    ) -> str:
        """Constructs the status line (Http version + status code + status detail)."""
        status_line = f"HTTP/{http_version} {status_code} {reason}"
        return status_line

    @staticmethod
    def construct_response_headers(headers: Mapping) -> str:
        """
        Construct headers as plain text from mapping of headers and their
        values.
        """
        headers_text = ""
        for header, value in headers.items():
            headers_text += f"{str(header).title()}: {value}\r\n"
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


class ServerResponseHandler(HttpParser):
    """
    The class responsible for sending requests to the remote server and
    handling them.
    """

    @staticmethod
    def construct_remote_server_url(asked_url: str):
        """Constructs the remote server url for sending requests to it."""
        return settings.proxy_settings['REQUESTED_URL'] + asked_url

    def get_modified_response_from_remote_server(self, user_request: UserRequest) -> bytes:
        """
        Sends a request to the remote server and returns a modified server
        response if it is necessary.
        """
        server_response_data = self.send_user_request_to_server(user_request)
        status_line, headers, content = self.get_and_modify_server_response(server_response_data)
        return self.construct_http_response(status_line, headers, content)

    def send_user_request_to_server(self, user_request: UserRequest) -> Response:
        """Sends the client request to the remote server with changed url."""
        server_response_data = requests.request(
            user_request.method,
            self.construct_remote_server_url(user_request.url),
            headers=user_request.headers,
        )
        return server_response_data

    def get_and_modify_server_response(self, server_response_data: Response) -> HttpParts:
        """
        Returns three parts of the server response: status line, headers
        and content. Headers and content are modified.
        """
        status_line = self.construct_response_status_line(
            server_response_data.status_code, server_response_data.reason
        )
        content = self.modify_response_content(
            server_response_data.content, server_response_data.headers
        )
        modified_headers = self.modify_response_headers(
            content, server_response_data.headers
        )
        headers_as_text = self.construct_response_headers(modified_headers)
        return HttpParts(status_line, headers_as_text, content)

    def modify_response_content(self, content: bytes, headers: CaseInsensitiveDict) -> bytes:
        """
        Modifies a content of the response if it is type of `text/html`. Otherwise,
        returns how it was passed.
        """
        content_type_of_response = headers.get("Content-Type")
        if content_type_of_response and 'text/html' in content_type_of_response:
            content = self.modify_words_in_html(content)
        return content

    @staticmethod
    def modify_words_in_html(html_content: bytes) -> bytes:
        """
        Modifies all 6-length words in html with adding specific character
        in the end.
        """
        soup = BeautifulSoup(html_content.decode(), "html.parser")
        for e in soup.find_all(text=True):
            res = re.sub(
                r'(\b[a-zA-z0-9]{' + str(settings.text_modifying['WORDS_LENGTH']) + r'}\b)',
                r'\1' + settings.text_modifying['ADD_CHARACTER'],
                e.string
            )
            e.string.replace_with(res)
        return str(soup).encode()

    @staticmethod
    def modify_response_headers(content: bytes, headers: CaseInsensitiveDict) -> CaseInsensitiveDict:
        """
        Modifies headers. Set a `Content-Length` header and removes the transfer
        and the content encoding, if it was provided because we have already
        decoded and have received full server response.
        """
        headers.pop('Transfer-Encoding', False)
        headers.pop('Content-Encoding', False)
        headers.update({'Content-Length': len(content)})
        return headers


class UserRequestHandler(HttpParser):
    """
    The class responsible for parsing and providing user's request
    in the appropriate form.
    """

    def parse_http_request(self, request_text: bytes | str) -> UserRequest:
        """
        Parses a plain request text and returns appropriate
        information about it. (Assumes the request doesn't have a body part).
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
        remote_server_host = self.get_host_from_remote_server_url()
        host_with_port_pattern = f"{settings.proxy_settings['HOST']}:{settings.proxy_settings['PORT']}"
        return re.sub(host_with_port_pattern, remote_server_host, user_request)

    @staticmethod
    def get_host_from_remote_server_url():
        """
        Returns host from the remote server url or raises an error if
        url is invalid.
        """
        remote_server_host = re.search(r"(?<=://).*", settings.proxy_settings['REQUESTED_URL'].strip())
        if not remote_server_host:
            raise ValueError(
                f"`{settings.proxy_settings['REQUESTED_URL']}` is a wrong `REQUESTED_URL` value."
            )
        return remote_server_host.group()


class ProxyHandler(StreamRequestHandler, ServerResponseHandler, UserRequestHandler):
    """
    The class responsible for handling requests from the client to the
    remote server and for processing server's responses and sending them
    back to the user.
    """

    def handle(self):
        """
        Handles the request from the client and returns a server response
        to him.
        """
        user_request = self.get_user_request()
        server_response = self.get_modified_response_from_remote_server(user_request)
        self.send_to_user(server_response)

    def send_to_user(self, message: bytes):
        """Sends a message to the user."""
        self.wfile.write(message)

    def get_user_request(self) -> UserRequest:
        """Returns information about user's request."""
        request_as_plain_text = self.get_plain_text_of_user_request(self.rfile)
        request_with_changed_host = self.change_host_in_user_request(request_as_plain_text)
        return self.parse_http_request(request_with_changed_host)
