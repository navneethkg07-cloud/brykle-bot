# Brykle Finance Discord Bot

A production-ready Discord finance bot built with Python, discord.py, gspread, and Google Service Account authentication for Brykle.

## Features
- Accounts tracking with `!invest`, `!spent`, `!reimburse`, `!balance`, `!business`, and `!history`
- Stock management with `!stockadd`, `!stockremove`, and `!stock`
- In-memory pending orders with `!order` and `!orders`
- Sales logging with `!sold`
- Friendly Discord embeds for success, errors, and information

## Project Structure
- `bot.py` — bot entrypoint
- `config.py` — environment-driven configuration
- `commands/` — command cogs for accounts, stock, orders, and sales
- `utils/` — reusable helpers, embeds, and Google Sheets access

## Environment Variables
Create a `.env` file with:
- `TOKEN`
- `CREDS_JSON`
- `ACCOUNTS_SHEET_ID`
- `SALES_SHEET_ID`
- `STOCK_SHEET_ID`

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running Locally
```bash
python bot.py
```

## Discord Bot Setup
1. Create a Discord application and bot in the Discord Developer Portal.
2. Enable the `Message Content Intent`.
3. Invite the bot to your server with the appropriate permissions.
4. Set the bot token in `TOKEN`.

## Google Sheets Setup
1. Create a Google Cloud project.
2. Enable the Google Sheets API and Google Drive API.
3. Create a service account and download the JSON key.
4. Paste the full JSON content into `CREDS_JSON`.
5. Share the target spreadsheets with the service account email.

## Example Commands
```text
!invest Navaneeth 10000 Initial Fund
!spent Navaneeth 1200 Filament
!reimburse Navaneeth 500 Petrol
!balance
!business
!history Navaneeth
!stockadd 25 Groot
!stockremove 2 Groot
!stock
!order Aditya 2 Groot for 80
!orders
!sold Aditya 2 Groot
!sold Aditya Groot for 80
```

## Railway Deployment
1. Push the repository to GitHub.
2. Create a new Railway project and connect the repository.
3. Set the environment variables above in Railway.
4. Deploy using the included Procfile and runtime configuration.

## Troubleshooting
- Ensure `TOKEN` is set before starting the bot.
- Ensure `CREDS_JSON` is valid JSON.
- Ensure the service account has access to the Sheets.
- If the bot starts in local fallback mode, verify the credentials are configured.
