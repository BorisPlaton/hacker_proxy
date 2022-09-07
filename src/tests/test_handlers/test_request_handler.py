import pytest

from proxy.handlers import UserRequest


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
def test_change_host_in_user_request_with_settings_value(proxy_settings, header, request_handler):
    host_header = f"{header}{proxy_settings['HOST']}:{proxy_settings['PORT']}"
    proxy_settings['REQUESTED_URL'] = 'https://news.ycombinator.com'
    remote_server_host = 'news.ycombinator.com'
    assert request_handler.change_host_in_user_request(host_header) == f"{header}{remote_server_host}"


@pytest.mark.parametrize(
    'wrong_remote_server_url', [
        'https:/news.ycombinator.com',
        'https//news.ycombinator.com',
        'httpsews.ycombinator.com',
        'g ',
        's',
        'Host: ',
        'Host:',
        '',
    ]
)
def test_change_host_in_user_request_with_wrong_settings_value(
        wrong_remote_server_url, proxy_settings, request_handler
):
    proxy_settings['REQUESTED_URL'] = wrong_remote_server_url
    host_header = f"Host: {proxy_settings['HOST']}:{proxy_settings['PORT']}"
    with pytest.raises(ValueError):
        request_handler.change_host_in_user_request(host_header)


def test_headers_plain_text_parsing(request_handler):
    headers_text = """
Host: https://news.ycombinator.com\r
User-Agent: curl/7.81.0\r
Accept: */*\r
Content-Length: 34\r
Content-Type: application/x-www-form-urlencoded\r
    """
    parsed_headers = request_handler.get_headers_dict(headers_text)
    expected_parsed_headers = {
        "Host": "https://news.ycombinator.com",
        "User-Agent": "curl/7.81.0",
        "Accept": "*/*",
        "Content-Length": "34",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    assert parsed_headers == expected_parsed_headers


def test_parsing_user_request(request_handler):
    user_request = """
POST /hello.123141 HTTP/1.1
Host: 127.0.0.1:8888
User-Agent: curl/7.81.0
Accept: */*
    """
    user_request_data = request_handler.parse_http_request(user_request)
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
