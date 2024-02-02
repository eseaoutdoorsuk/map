import os, json
from dotenv import load_dotenv; load_dotenv()
from google.oauth2 import service_account
import gspread
from collections import defaultdict
from enum import Enum

AUTH_LEVEL = Enum('AUTH_LEVEL', ['PUBLIC', 'MEMBERS', 'DEV', 'DENIED'])
DEFAULT_LOCATION = "10,10"

def get_spreadsheet():
    client = gspread.authorize(
        service_account.Credentials.from_service_account_info(
            json.loads(os.getenv("GOOGLE_JSON"))
        ).with_scopes(
            ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        )
    )
    return client.open_by_url(os.getenv("GOOGLE_SPREADSHEET"))

def read_spreadsheet(spreadsheet: gspread.Spreadsheet, sheet="Sheet1"):
    return spreadsheet.worksheet(sheet).get_all_records()

def write_spreadsheet(rows, spreadsheet: gspread.Spreadsheet, sheet="Sheet1"):
    if len(rows) > 0:
        spreadsheet.worksheet(sheet).append_rows(rows)
    status = f"Written {len(rows)} rows to sheet: {sheet}"
    print(status)
    return status

def get_users_from_records(records, locations, auth_level=AUTH_LEVEL.PUBLIC):
    location_dict = defaultdict(lambda: DEFAULT_LOCATION, {
        loc["location"]: loc["latlon"] for loc in locations
    })
    return [
        {
            "name": redact_name(record["Name"], auth_level=auth_level, filter1=record["map1"], filter2=record["map2"]),
            "locations": [{
                "name": location.title(),
                "coords": location_dict[location]
                } for location in split_location_text(record["location_clean"])],
            "phone": redact_phone(record["number_clean"], auth_level=auth_level, filter1=record["map1"], filter2=record["map2"]),
        } 
        for record in records if record["wa"] is True
    ]

def redact_phone(phone, auth_level=AUTH_LEVEL.PUBLIC, filter1=0, filter2=0):
    phone = str(phone).strip()
    if auth_level in (AUTH_LEVEL.PUBLIC, AUTH_LEVEL.DENIED):
        return ""
    elif auth_level == AUTH_LEVEL.MEMBERS:
        if filter2 in (0, 2):
            return "********" + phone[-3:]
        elif filter2 in (-1, 1, 3):
            return ""
    elif auth_level == AUTH_LEVEL.DEV:
        return phone
    else:
        raise ValueError("auth_level invalid")

def split_location_text(location_text):
    return [location.lower() for location in location_text.split("/")]

def redact_name(name, auth_level=AUTH_LEVEL.PUBLIC, filter1=0, filter2=0):
    name = str(name).strip()
    first_letter = f"{name[:1]}.".upper()
    if auth_level in (AUTH_LEVEL.PUBLIC, AUTH_LEVEL.DENIED):
        if filter1 == 1:
            return first_letter
        elif filter1 in (0, -1):
            return "Anonymous"
    elif auth_level == AUTH_LEVEL.MEMBERS:
        if filter2 in (-1, 2, 3):
            return "Anonymous"
        elif filter2 in (0, 1):
            return first_letter
    elif auth_level == AUTH_LEVEL.DEV:
        return name
    else:
        raise ValueError("auth_level invalid")
