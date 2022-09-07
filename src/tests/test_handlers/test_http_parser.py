import pytest

from configuration.settings import settings
from tests.utils import get_path_to_source_file


@pytest.mark.parametrize(
    "server_url, asked_url",
    [
        ('', ''),
        ('fafagh/', '/item?helloworld=true'),
        ('https://fafa', '/'),
        ('http://fafa', '///'),
    ]
)
def test_remote_server_url_constructing(http_parser, server_url, asked_url):
    http_parser.proxy_settings['REQUESTED_URL'] = server_url
    assert http_parser.construct_remote_server_url(asked_url) == server_url + asked_url


def test_proxy_settings_property_is_key_of_settings_dict(http_parser):
    assert http_parser.proxy_settings is settings['PROXY_SERVER']


@pytest.mark.parametrize(
    "status_code, reason, http_version",
    [
        ('', '', ''),
        ('1', '/item?helloworld=true', '2'),
        (2, '/', '3'),
        ('b', 'ok', '0.9'),
        (404, 'not found', 0.9),
    ]
)
def test_constructing_status_line(http_parser, status_code, reason, http_version):
    assert http_parser.construct_response_status_line(status_code, reason, http_version) == \
           f"HTTP/{http_version} {status_code} {reason}"


def test_constructing_status_line_default_http_method_is_1_1(http_parser):
    assert http_parser.construct_response_status_line(200, 'OK') == "HTTP/1.1 200 OK"


def test_constructing_headers_text(http_parser):
    headers_dict = {
        1: 2,
        "hello": 'world',
        'Host': "localhost",
        "port": 8888,
        "Content-Length": 0,
        "true": False
    }
    headers_as_text = '\r\n'.join(
        ["1: 2", "Hello: world", "Host: localhost", "Port: 8888",
         "Content-Length: 0", "True: False"]
    ) + '\r\n'
    assert http_parser.construct_response_headers(headers_dict) == headers_as_text


@pytest.mark.parametrize(
    "status_line, headers, content",
    [
        ('HTTP/1.1 200 OK', 'Content-Length: 0', b''),
        ('1', '/item?helloworld=true', b'2'),
        ('32', '/', b'3'),
        ('b', 'ok', b'0.9'),
        ('', '', b''),
    ]
)
def test_constructing_http_response(http_parser, status_line, headers, content):
    http_response = (
            status_line.encode() +
            b'\r\n' +
            headers.encode() +
            b'\r\n' +
            b'\r\n' +
            content
    )
    assert http_parser.construct_http_response(status_line, headers, content) == http_response


@pytest.mark.parametrize(
    "http_part",
    [
        '\n',
        '\r',
        '',
        'h',
    ]
)
def test_http_part_without_crlf_must_be_added_crlf(http_parser, http_part):
    assert http_parser.set_http_part_ends_with_crlf(http_part) == http_part + '\r\n'


@pytest.mark.parametrize(
    "http_part",
    [
        '\r\n',
        '\r\r\r\n',
        'h\r\n',
    ]
)
def test_http_part_with_crlf_must_not_be_added_crlf(http_parser, http_part):
    assert http_parser.set_http_part_ends_with_crlf(http_part) == http_part


@pytest.mark.parametrize(
    "fake_socket_file",
    [
        'fake_server_socket.txt',
        'fake_server_socket2.txt',
    ]
)
def test_plain_text_of_server_socket_accepts_only_binary_io(http_parser, fake_socket_file):
    with pytest.raises(ValueError):
        with open(get_path_to_source_file('test_handlers', 'source', fake_socket_file)) as server_socket:
            assert http_parser.get_plain_text_of_user_request(server_socket) == ''.join(server_socket.readlines())


@pytest.mark.parametrize(
    "fake_socket_file",
    [
        'fake_server_socket.txt',
        'fake_server_socket2.txt',
    ]
)
def test_plain_text_of_server_socket_accepts_only_binary_io(http_parser, fake_socket_file):
    with pytest.raises(ValueError):
        with open(get_path_to_source_file('test_handlers', 'source', fake_socket_file)) as server_socket:
            assert http_parser.get_plain_text_of_user_request(server_socket) == ''.join(server_socket.readlines())


@pytest.mark.parametrize(
    "fake_socket_file",
    [
        'fake_server_socket.txt',
        'fake_server_socket2.txt',
    ]
)
def test_plain_text_of_server_socket_returned_by_parser(http_parser, fake_socket_file):
    path_to_fake_socket = get_path_to_source_file('test_handlers', 'source', fake_socket_file)
    with open(path_to_fake_socket, 'rb') as server_socket, open(path_to_fake_socket) as file_data:
        assert (
                http_parser.get_plain_text_of_user_request(server_socket) ==
                '\r\n'.join([line.strip() for line in file_data.readlines()])
        )
