import pytest
from scrapper import AppleJobScrapper
import requests


def test_extract_success(mocker):
    mock_response = mocker.Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.text = """<html><head><title>Test Page</title></head><body><span>Test Content</span></body></html>"""
    mocker.patch("requests.get", return_value=mock_response)

    apple_job_scrapper = AppleJobScrapper()
    page_title, page_content = apple_job_scrapper.extract("http://example.com")
    assert page_title == "Test Page"
    assert page_content.strip() == "Test Content"


def test_extract_failure_invalid_url(mocker):
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException)
    apple_job_scrapper = AppleJobScrapper()
    with pytest.raises(requests.exceptions.RequestException):
        apple_job_scrapper.extract("http://example.com")


def test_extract_failure_partial_content(mocker):
    mock_response = mocker.Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.text = """<html><head><title>Test Page</title></head><body>"""
    mocker.patch("requests.get", return_value=mock_response)
    apple_job_scrapper = AppleJobScrapper()
    page_title, page_content = apple_job_scrapper.extract("http://example.com")
    assert page_title is not None
    assert len(page_content) == 0
