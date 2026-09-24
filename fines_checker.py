#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "playwright",
# ]
# ///
"""Automated traffic-fines inquiry tool (v2).

Drives the Egyptian traffic portal (ppo.gov.eg) with Playwright, fills in the
vehicle plate and national ID, captures a screenshot of the violations summary,
and optionally forwards it through WhatsApp (via the mudslide CLI).

No personal data is stored in this file. All values are supplied at runtime:

    python fines_checker.py \
        --number 123 \
        --letters ا ب ج \
        --national-id 12345678901234 \
        --recipient 201000000000 \
        --save-dir screenshots
"""

import argparse
import asyncio
import os
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright

DEFAULT_SAVE_DIR = "screenshots"
PORTAL_URL = "https://ppo.gov.eg/ppo/r/ppoportal/ppoportal/traffic"


def parse_args():
    parser = argparse.ArgumentParser(description="Traffic fines inquiry & notification tool")
    parser.add_argument("--number", required=True, help="Vehicle plate number (digits)")
    parser.add_argument("--letters", nargs="+", required=True,
                        help="Vehicle plate letters in field order (e.g. ا ب ج)")
    parser.add_argument("--national-id", required=True, help="National ID used for the inquiry")
    parser.add_argument("--recipient", default="",
                        help="WhatsApp recipient number to send the screenshot to (skip to disable)")
    parser.add_argument("--caption", default="Traffic fines check", help="WhatsApp caption")
    parser.add_argument("--save-dir", default=DEFAULT_SAVE_DIR, help="Directory to store screenshots")
    parser.add_argument("--headful", action="store_true", help="Show the browser window (debugging)")
    return parser.parse_args()


async def run_inquiry(args):
    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not args.headful)
        page = await (await browser.new_context()).new_page()

        print("1. Navigating to the traffic portal...")
        await page.goto(PORTAL_URL, wait_until="networkidle")

        try:
            try:
                await page.click("text=المخالفات", timeout=5000)
                await asyncio.sleep(2)
                await page.click("text=استعلام", timeout=5000)
                await asyncio.sleep(2)
                await page.click("text=مخالفات رخص المركبات", timeout=5000)
                await asyncio.sleep(2)
            except Exception:
                print("Notice: direct navigation or links already active.")

            print("Selecting 'Letters and Numbers' (حروف وأرقام)...")
            await page.click("label[for='P14_CHOSE_OPTION_0']")
            await asyncio.sleep(5)

            print("2. Entering plate details...")
            await page.locator('#P14_NUMBER_WITH_LETTER').wait_for(state="visible", timeout=30000)
            await page.locator('#P14_NUMBER_WITH_LETTER').press_sequentially(args.number, delay=100)
            await asyncio.sleep(2)
            letter_fields = ['#P14_LETER_1', '#P14_LETER_2', '#P14_LETER_3']
            for letter, field in zip(args.letters, letter_fields):
                await page.locator(field).press_sequentially(letter, delay=100)
                await asyncio.sleep(2)

            print("3. Entering National ID...")
            nat_id_input = page.locator('#P14_NATIONAL_ID_NUMS_LETTERS')
            await nat_id_input.wait_for(state="visible", timeout=30000)
            await nat_id_input.press_sequentially(args.national_id, delay=100)

            print("4. Requesting total violations...")
            await page.locator('#GET_FIN_LETTER_NUMBERS_BTN').wait_for(state="visible", timeout=30000)
            await page.locator('#GET_FIN_LETTER_NUMBERS_BTN').click()

            print("5. Waiting for results to load...")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(10000)

            print("6. Taking screenshot of summary...")
            screenshot_path = os.path.join(str(save_dir), f"fines_{args.number}.png")
            await page.screenshot(path=screenshot_path, full_page=False)
            print(f"Saved to {screenshot_path}")

            if args.recipient:
                print(f"7. Sending to WhatsApp ({args.recipient})...")
                send_command = (
                    f"npx mudslide send-image {args.recipient} {screenshot_path} "
                    f"--caption '{args.caption}'"
                )
                for attempt in range(1, 3):
                    result = subprocess.run(send_command, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        print("WhatsApp message sent successfully!")
                        break
                    print(
                        f"WhatsApp attempt {attempt} failed: "
                        f"{result.stderr or result.stdout}. Retrying in 4s..."
                    )
                    await asyncio.sleep(4)
            else:
                print("No recipient given, skipping WhatsApp notification.")

        except Exception as exc:
            print(f"An error occurred: {exc}")
            error_path = os.path.join(str(save_dir), f"fines_{args.number}_error.png")
            await page.screenshot(path=error_path, full_page=False)

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_inquiry(parse_args()))