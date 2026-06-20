"""Test the tax point calculator page."""
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).parent.parent
FILE_URL = f"file:///{PROJECT_ROOT / 'tools' / 'tax-calc' / 'index.html'}"


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=3,
        )
        page = context.new_page()
        page.goto(FILE_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)

        errors = []

        # Test 1: Page loads with title
        title = page.title()
        if not title:
            errors.append("Page title is empty")
        else:
            print(f"[OK] Page title: {title}")

        # Test 2: Amount input exists
        amount_input = page.locator("#amountInput")
        if amount_input.count() != 1:
            errors.append("Amount input #amountInput not found")
        else:
            print("[OK] Amount input found")

        # Test 3: Tax rate dropdown exists with options including custom
        rate_select = page.locator("#rateSelect")
        if rate_select.count() != 1:
            errors.append("Rate select #rateSelect not found")
        else:
            options = rate_select.locator("option")
            count = options.count()
            if count < 6:
                errors.append(f"Expected at least 6 options (5 rates + custom), got {count}")
            else:
                print(f"[OK] Rate select has {count} options")

        # Test 4: Custom rate input hidden by default
        custom_input = page.locator("#customRateInput")
        if custom_input.count() != 1:
            errors.append("Custom rate input #customRateInput not found")
        elif custom_input.is_visible():
            errors.append("Custom rate input should be hidden by default")
        else:
            print("[OK] Custom rate input hidden by default")

        # Test 5: Select "custom" shows custom input
        rate_select.select_option("custom")
        page.wait_for_timeout(200)
        if not custom_input.is_visible():
            errors.append("Custom rate input should be visible after selecting custom")
        else:
            print("[OK] Custom rate input shown when custom selected")

        # Test 6: Calculation correctness — 含税 11300, 税率 13%
        rate_select.select_option("0.13")
        page.wait_for_timeout(100)
        amount_input.fill("11300")
        page.wait_for_timeout(200)

        pre_tax = page.locator("#preTaxAmount")
        tax_amount = page.locator("#taxAmount")
        if pre_tax.count() != 1:
            errors.append("Pre-tax amount element #preTaxAmount not found")
        if tax_amount.count() != 1:
            errors.append("Tax amount element #taxAmount not found")
        else:
            pre_tax_text = pre_tax.inner_text()
            tax_amount_text = tax_amount.inner_text()
            if "10000" not in pre_tax_text:
                errors.append(f"Expected pre-tax ~10000, got '{pre_tax_text}'")
            else:
                print(f"[OK] Pre-tax amount: {pre_tax_text}")
            if "1300" not in tax_amount_text:
                errors.append(f"Expected tax ~1300, got '{tax_amount_text}'")
            else:
                print(f"[OK] Tax amount: {tax_amount_text}")

        # Test 7: Calculation with 5% rate — 含税 10500
        rate_select.select_option("0.05")
        page.wait_for_timeout(100)
        amount_input.fill("10500")
        page.wait_for_timeout(200)
        pre_tax_text = pre_tax.inner_text()
        tax_amount_text = tax_amount.inner_text()
        if "10000" not in pre_tax_text:
            errors.append(f"5% test: Expected pre-tax ~10000, got '{pre_tax_text}'")
        else:
            print(f"[OK] 5% Pre-tax: {pre_tax_text}")
        if "500" not in tax_amount_text:
            errors.append(f"5% test: Expected tax ~500, got '{tax_amount_text}'")
        else:
            print(f"[OK] 5% Tax: {tax_amount_text}")

        # Test 8: Copy buttons exist
        copy_btns = page.locator(".copy-btn")
        if copy_btns.count() < 2:
            errors.append(f"Expected at least 2 copy buttons, got {copy_btns.count()}")
        else:
            print(f"[OK] {copy_btns.count()} copy buttons found")

        # Test 9: Back link exists
        back_link = page.locator("a.back-link")
        if back_link.count() != 1:
            errors.append("Back link a.back-link not found")
        else:
            href = back_link.get_attribute("href")
            if href != "../../index.html":
                errors.append(f"Back link href expected '../../index.html', got '{href}'")
            else:
                print(f"[OK] Back link: {href}")

        if errors:
            print(f"\n=== {len(errors)} ERROR(S) ===")
            for e in errors:
                print(f"  FAIL: {e}")
            browser.close()
            raise SystemExit(1)
        else:
            print("\n=== ALL TESTS PASSED ===")
            browser.close()


if __name__ == "__main__":
    run()
