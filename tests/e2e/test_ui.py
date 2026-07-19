import pytest
import os
import httpx
from playwright.sync_api import Page, expect

# Since UI tests depend on the frontend server, we skip them by default unless specifically requested,
# or we can mock/run them. Here we write the standard Playwright tests for F7, F8, F9, F10.

@pytest.mark.skipif(
    os.getenv("RUN_UI_TESTS") != "true",
    reason="UI tests require a running frontend server. Set RUN_UI_TESTS=true to execute."
)
def test_ui_onboarding_guideline_modal(page: Page):
    """F7: Onboarding Guideline manual pop-up interceptor.
    
    Verifies that first-time login displays a modal locking the dashboard,
    which cannot be dismissed without checking the 'OK' acknowledgment checkbox.
    """
    # 1. Navigate to the login page and authenticate
    page.goto("http://localhost:3000/login")
    page.fill("input[type='email']", "farmer_f7@e2e.test")
    page.fill("input[type='password']", "Password@123")
    page.click("button[type='submit']")

    # 2. Assert dashboard is loaded but locked by the guideline modal
    page.wait_for_selector(".guideline-modal-overlay")
    expect(page.locator(".guideline-modal-overlay")).to_be_visible()
    
    # Assert dashboard links or buttons are blocked/disabled
    dashboard_button = page.locator("button:has-text('Register Crop')")
    expect(dashboard_button).to_be_disabled()

    # 3. Attempt to click dismiss/OK without checking the checkbox
    dismiss_button = page.locator("button:has-text('Acknowledge & Continue')")
    dismiss_button.click()
    # Modal should still be visible
    expect(page.locator(".guideline-modal-overlay")).to_be_visible()

    # 4. Check the "OK" checkbox and click acknowledge
    page.click("input[type='checkbox']#guideline-ack")
    dismiss_button.click()

    # 5. Assert modal is removed from DOM and dashboard becomes interactive
    expect(page.locator(".guideline-modal-overlay")).not_to_be_visible()
    expect(dashboard_button).to_be_enabled()


@pytest.mark.skipif(
    os.getenv("RUN_UI_TESTS") != "true",
    reason="UI tests require a running frontend server. Set RUN_UI_TESTS=true to execute."
)
def test_ui_pdf_assets_and_about_page(page: Page):
    """F8: Guideline manual PDF assets and About page rendering."""
    # 1. Navigate to About Page
    page.goto("http://localhost:3000/about")
    
    # Assert main texts are present
    expect(page.locator("h1")).to_contain_text("About AgriTrace")
    expect(page.locator("body")).to_contain_text("Terms & Conditions")

    # 2. Intercept static PDF manual asset loading
    # Request the static PDF manual asset directly
    with page.expect_response("**/assets/guideline_manual.pdf") as response_info:
        page.goto("http://localhost:3000/assets/guideline_manual.pdf")
        
    response = response_info.value
    assert response.status == 200
    assert "application/pdf" in response.headers.get("content-type", "")


@pytest.mark.skipif(
    os.getenv("RUN_UI_TESTS") != "true",
    reason="UI tests require a running frontend server. Set RUN_UI_TESTS=true to execute."
)
def test_ui_interactive_walkthrough_tour(page: Page):
    """F9: Interactive walkthrough onboarding tour.
    
    Verifies step-by-step navigation (Next, Back, Skip, Finish) of the user onboarding tour.
    """
    page.goto("http://localhost:3000/dashboard")
    
    # Trigger tour manually if not auto-started
    page.click("button:has-text('Start Tour')")
    
    # Step 1 visible
    expect(page.locator(".onboarding-tour-step-1")).to_be_visible()
    
    # Click Next -> Step 2
    page.click("button:has-text('Next')")
    expect(page.locator(".onboarding-tour-step-2")).to_be_visible()
    expect(page.locator(".onboarding-tour-step-1")).not_to_be_visible()

    # Click Back -> Step 1
    page.click("button:has-text('Back')")
    expect(page.locator(".onboarding-tour-step-1")).to_be_visible()

    # Click Next -> Step 2
    page.click("button:has-text('Next')")
    
    # Click Skip -> Tour ends
    page.click("button:has-text('Skip')")
    expect(page.locator(".onboarding-tour-step-2")).not_to_be_visible()


@pytest.mark.skipif(
    os.getenv("RUN_UI_TESTS") != "true",
    reason="UI tests require a running frontend server. Set RUN_UI_TESTS=true to execute."
)
def test_ui_contrast_legibility_audit(page: Page):
    """F10: Theme accessibility contrast legibility audit.
    
    Toggles themes and audits color contrast using axe-core.
    """
    # Import axe-core for Playwright if available
    try:
        from axe_playwright_python.sync_playwright import Axe
    except ImportError:
        pytest.skip("axe-playwright-python is not installed. Skipping legibility audit.")

    page.goto("http://localhost:3000/dashboard")

    # 1. Audit Light Theme
    page.click("button#theme-light")
    results_light = Axe().run(page)
    # Check for color contrast violations (WCAG AA rule: color-contrast)
    violations_light = [v for v in results_light.violations if v["id"] == "color-contrast"]
    assert len(violations_light) == 0, f"Contrast violations in Light theme: {violations_light}"

    # 2. Audit Dark Theme
    page.click("button#theme-dark")
    results_dark = Axe().run(page)
    violations_dark = [v for v in results_dark.violations if v["id"] == "color-contrast"]
    assert len(violations_dark) == 0, f"Contrast violations in Dark theme: {violations_dark}"
