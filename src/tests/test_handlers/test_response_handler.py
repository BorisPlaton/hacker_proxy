import pytest
import requests

from configuration.settings import settings
from proxy.handlers import UserRequest


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


@pytest.mark.parametrize(
    "original_text, modified_text", [
        (
                "Если задачу удалось сделать быстро, и у вас еще остался энтузиазм - как насчет написания тестов?",
                "Если задачу™ удалось сделать быстро™, и у вас еще остался энтузиазм - как насчет™ написания тестов™?"
        ),
        ("Через ваш прокси:", "Через ваш прокси™:"),
        (
                """The visual description of the colliding files, at
                http://shattered.io/static/pdf_format.png, is not very helpful
                in understanding how they produced the PDFs, so I took apart
                the PDFs and worked it out.
                Basically, each PDF contains a single large (421,385-byte) JPG
                image, followed by a few PDF commands to display the JPG. The
                collision lives entirely in the JPG data - the PDF format is
                merely incidental here. Extracting out the two images shows two
                JPG files with different contents (but different SHA-1 hashes
                since the necessary prefix is missing). Each PDF consists of a
                common prefix (which contains the PDF header, JPG stream
                descriptor and some JPG headers), and a common suffix (containing
                image data and PDF display commands).""",
                """The visual™ description of the colliding files, at
                http://shattered.io/static/pdf_format.png, is not very helpful
                in understanding how they produced the PDFs, so I took apart
                the PDFs and worked™ it out.
                Basically, each PDF contains a single™ large (421,385-byte) JPG
                image, followed by a few PDF commands to display the JPG. The
                collision lives entirely in the JPG data - the PDF format™ is
                merely™ incidental here. Extracting out the two images™ shows two
                JPG files with different contents (but different SHA-1 hashes™
                since the necessary prefix™ is missing). Each PDF consists of a
                common™ prefix™ (which contains the PDF header™, JPG stream™
                descriptor and some JPG headers), and a common™ suffix™ (containing
                image data and PDF display commands)."""
        )
    ]
)
def test_modifying_html(response_handler, original_text, modified_text):
    assert response_handler.modify_words_in_html(original_text).decode() == modified_text


@pytest.mark.webtest
def test_modified_response(response_handler):
    modified_words = [
        "visual™", "worked™", "single™", "format™", "merely™", "images™",
        "common™", "prefix™", "header™", "stream™", "suffix™"
    ]
    original_response = requests.get(" https://news.ycombinator.com/item?id=13713480")
    _, _, content = response_handler.get_and_modify_server_response(original_response)
    content_in_string = content.decode()
    for word in modified_words:
        assert word in content_in_string


@pytest.mark.webtest
def test_request_is_sent_to_remote_server(response_handler):
    remote_url = '/item?id=13713480'
    settings.proxy_settings['REQUESTED_URL'] = 'https://news.ycombinator.com'
    original_response = requests.get(f'https://news.ycombinator.com{remote_url}')
    user_request = UserRequest(headers={}, http_version='1.1', method='get', url=remote_url)
    assert original_response.content == response_handler.send_user_request_to_server(user_request).content
