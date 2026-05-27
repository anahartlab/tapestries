import gspread
from google.oauth2.service_account import Credentials

# ---------- CONFIG ----------
GOOGLE_SHEET_ID = "1uHX5hZWX6uLooTnU7ao_xocRIkckWxqFp4cQI65BZNc"

SOURCE_SHEET = "paintings"

TARGET_SHEETS = [
    "hindu",
    "abstract",
    "fantasy",
    "popart"
]

SERVICE_ACCOUNT_FILE = "/Users/anahart/keys/google-sa.json"

# ---------- GOOGLE AUTH ----------
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=scopes
)

gc = gspread.authorize(creds)

# ---------- OPEN TABLE ----------
sh = gc.open_by_key(GOOGLE_SHEET_ID)

ws_source = sh.worksheet(SOURCE_SHEET)

# ---------- READ PAINTINGS ----------
source_values = ws_source.get_all_values()

source_header = source_values[0]
source_rows = source_values[1:]

idx_source_name = source_header.index("Name")
idx_source_stock = source_header.index("Stock")

# создаем словарь:
# {
#   "OWLS GORIZONT": "текст stock"
# }

stock_map = {}

for row in source_rows:

    if len(row) <= idx_source_stock:
        continue

    name = row[idx_source_name].strip()
    stock = row[idx_source_stock].strip()

    if name:
        stock_map[name] = stock

# ---------- UPDATE TARGET SHEETS ----------
for sheet_name in TARGET_SHEETS:

    ws = sh.worksheet(sheet_name)

    values = ws.get_all_values()

    if not values:
        continue

    header = values[0]
    rows = values[1:]

    idx_name = header.index("Name")

    # создаем Stock если нет
    if "Stock" not in header:
        header.append("Stock")
        idx_stock = len(header) - 1

        for r in rows:
            r.append("")
    else:
        idx_stock = header.index("Stock")

    # ---------- UPDATE ROWS ----------
    for row in rows:

        while len(row) <= idx_stock:
            row.append("")

        name = row[idx_name].strip()

        if name in stock_map:
            row[idx_stock] = stock_map[name]

    # ---------- WRITE BACK ----------
    output = [header] + rows

    ws.clear()
    ws.update("A1", output)

    print(f"OK. Updated sheet: {sheet_name}")

print("DONE")