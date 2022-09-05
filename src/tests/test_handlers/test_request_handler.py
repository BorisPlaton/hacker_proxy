import pytest

from proxy.handlers import RequestHandler, UserRequest


@pytest.mark.parametrize(
    'header', [
        'header: : ',
        '1515',
        '',
        'g 1agaa',
        's',
        'gagaa314',
        'gagaa  ',
        'Host:',
        'Host: ',
        'HOST: ',
    ]
)
def test_change_host_in_user_request_with_settings_value(proxy_settings, header):
    host_header = f"{header}{proxy_settings['HOST']}:{proxy_settings['PORT']}"
    assert RequestHandler().change_host_in_user_request(host_header) == f"{header}{proxy_settings['REQUESTED_URL']}"


def test_headers_plain_text_parsing():
    headers_text = """
Host: https://news.ycombinator.com\r
User-Agent: curl/7.81.0\r
Accept: */*\r
Content-Length: 34\r
Content-Type: application/x-www-form-urlencoded\r
    """
    parsed_headers = RequestHandler().parse_headers_text(headers_text)
    expected_parsed_headers = {
        "Host": "https://news.ycombinator.com",
        "User-Agent": "curl/7.81.0",
        "Accept": "*/*",
        "Content-Length": "34",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    assert parsed_headers == expected_parsed_headers


def test_parsing_user_request():
    user_request = """
POST /hello.123141 HTTP/1.1
Host: 127.0.0.1:8888
User-Agent: curl/7.81.0
Accept: */*
    """
    user_request_data = RequestHandler().parse_user_request(user_request)
    user_request_data_expected = UserRequest(
        method='POST',
        url='/hello.123141',
        http_version='HTTP/1.1',
        headers={
            'Host': '127.0.0.1:8888',
            'User-Agent': 'curl/7.81.0',
            'Accept': '*/*',
        }
    )
    assert user_request_data == user_request_data_expected
