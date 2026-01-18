import pytest
import re
from playwright.sync_api import sync_playwright, expect
import requests

def is_server_running():
    try:
        requests.get("http://localhost:8000")
        return True
    except:
        return False

@pytest.mark.skipif(not is_server_running(), reason="Server not running")
def test_file_upload_ui_state():
    """
    Verify script.js logic:
    When #file-input changes:
      - #upload-content gets .hidden
      - #preview-img does NOT (it is inside #preview-wrapper which becomes visible)
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:8000")
        
        # 1. Select Domain (to reach playground)
        page.click("text=Automotive")
        
        # 2. Wait for playground
        page.wait_for_selector("#playground")
        
        # 3. Upload File
        # We trigger the file chooser logic by setting input files directly on the hidden input
        # This will fire the 'change' event which our script listens to.
        
        page.set_input_files("#file-input", {
            "name": "test_logo.jpg",
            "mimeType": "image/jpeg",
            "buffer": b"fake_image_content" 
        })
        
        # Playwright sometimes needs a small tick for the event to propagate if not awaited implicitly
        # but set_input_files awaits the action.
        page.wait_for_timeout(500) # Give UI a moment to react (remove .hidden)
        
        # 4. Assertions
        # #upload-content should be hidden
        expect(page.locator("#upload-content")).to_have_class(re.compile(r"hidden"))
        
        # #preview-img should be visible (and not have hidden class)
        expect(page.locator("#preview-img")).to_be_visible()
        expect(page.locator("#preview-img")).not_to_have_class(re.compile(r"hidden"))
        
        browser.close()
