# fines_checker

A credential-free **traffic-violations inquiry** tool for the Egyptian traffic portal
([ppo.gov.eg](https://ppo.gov.eg)). Drives the portal with Playwright, fills in a vehicle plate
number and national ID, screenshots the violations summary, and optionally forwards it via
WhatsApp. **No personal data lives in this repository** — all values are passed at runtime.

## Features

- Navigates the `ppo.gov.eg` portal and selects "Letters and Numbers".
- Types the plate digits + three Arabic letters and the national ID.
- Screenshots the violations summary to `screenshots/`.
- Sends the screenshot over WhatsApp (via the `mudslide` CLI) with a custom caption and retry.
- Saves an error snapshot if anything fails.

## Installation & Quick Start (v2)

### Option 1: Zero-Setup with `uv` (Recommended)
This tool supports PEP 723 inline metadata. You can run it instantly without creating a virtual environment or installing packages manually:

```bash
uv run fines_checker.py \
    --number 123 \
    --letters ا ب ج \
    --national-id 12345678901234 \
    --recipient 201000000000
```

### Option 2: Traditional `pip` / `venv`
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

```bash
python fines_checker.py \
    --number 123 \
    --letters ا ب ج \
    --national-id 12345678901234 \
    --recipient 201000000000 \
    --caption "Traffic fines check"
```

| Flag            | Required | Description                              |
|-----------------|----------|------------------------------------------|
| `--number`      | yes      | Vehicle plate number (digits)            |
| `--letters`     | yes      | Plate letters in field order (1–3)       |
| `--national-id` | yes      | National ID for the inquiry              |
| `--recipient`   | no       | WhatsApp recipient; omit = no sending    |
| `--caption`     | no       | Message caption (default: `Traffic fines check`) |
| `--save-dir`    | no       | Output folder (default: `screenshots/`)  |
| `--headful`     | no       | Show the browser window (debugging)      |

Run automatically with cron:

```cron
0 9 * * * cd /path/to/fines_checker && venv/bin/python fines_checker.py --number 123 --letters ا ب ج --national-id 12345678901234 --recipient 201000000000
```

## Repository details

- **Short description**: `Credential-free Egyptian traffic-fines lookup with WhatsApp notifications.`
- **Topics**: `automation`, `playwright`, `traffic-fines`, `whatsapp`, `python`, `cron`
- **License**: [MIT](https://opensource.org/licenses/MIT).

## Disclaimer

Use only for legitimate, personal inquiries in line with the portal's terms of service.