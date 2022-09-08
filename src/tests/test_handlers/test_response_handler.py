import pytest


@pytest.mark.parametrize(
    "server_url, asked_url",
    [
        ('', ''),
        ('fafagh/', '/item?helloworld=true'),
        ('https://fafa', '/'),
        ('http://fafa', '///'),
    ]
)
def test_remote_server_url_constructing(response_handler, server_url, asked_url, project_settings):
    project_settings.proxy_settings['REQUESTED_URL'] = server_url
    assert response_handler.construct_remote_server_url(asked_url) == server_url + asked_url
