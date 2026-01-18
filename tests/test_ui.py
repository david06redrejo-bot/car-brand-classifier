import pytest
from playwright.sync_api import sync_playwright, expect
import requests

def is_server_running():
    try:
        requests.get("http://localhost:8000")
        return True
    except:
        return False

skip_if_no_server = pytest.mark.skipif(not is_server_running(), reason="Server not running")

@skip_if_no_server
def test_homepage_loads():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:8000")
        assert page.title() == "OmniVision - Multi-Domain Recognition"
        browser.close()

@skip_if_no_server
def test_card_interaction():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:8000")
        
        # Check domain selector is visible
        selector = page.locator("#domain-selector")
        expect(selector).to_be_visible()
        
        # Click Cars
        page.click("text=Automotive")
        
        # Check transition
        # Selector hidden
        expect(selector).to_be_hidden()
        
        # Hero visible
        expect(page.locator("#hero")).to_be_visible()
        
        # Check theme class on body
        assert "theme-cars" in page.get_attribute("body", "class")
        
        browser.close()

@skip_if_no_server
def test_css_loading():
    import requests
    response = requests.get("http://localhost:8000/static/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["Content-Type"]
