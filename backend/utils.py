import os, json
from dotenv import load_dotenv; load_dotenv()
from google.oauth2 import service_account
import gspread
from collections import defaultdict
from enum import Enum

AUTH_LEVEL = Enum('AUTH_LEVEL', ['PUBLIC', 'MEMBERS', 'DEV', 'DENIED'])

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
    location_dict = defaultdict(lambda: "10,10", {
        loc["location"]: loc["latlon"] for loc in locations
    })
    return [
        {
            "name": redact_name(record["Name"], auth_level=auth_level),
            "locations": [{
                "name": location, #TODO capitalise
                "coords": location_dict[location]
                } for location in split_location_text(record["temp1"])],
            "phone": redact_phone(record["temp2"], auth_level=auth_level),
        } 
        for record in records
    ]

def redact_phone(phone, auth_level=AUTH_LEVEL.PUBLIC):
    phone = str(phone).strip()
    match auth_level:
        case AUTH_LEVEL.PUBLIC | AUTH_LEVEL.DENIED:
            return ""
        case AUTH_LEVEL.MEMBERS:
            return "********" + phone[-3:]
        case AUTH_LEVEL.DEV:
            return phone
        case _:
            raise ValueError("auth_level invalid")
    return 

def split_location_text(location_text):
    return [location.lower() for location in location_text.split("/")]

def redact_name(name, auth_level=AUTH_LEVEL.PUBLIC):
    name = str(name).strip()
    match auth_level:
        case AUTH_LEVEL.PUBLIC | AUTH_LEVEL.DENIED:
            return f"{name[:1]}."
        case AUTH_LEVEL.MEMBERS:
            return name.split(" ")[0]
        case AUTH_LEVEL.DEV:
            return name
        case _:
            raise ValueError("auth_level invalid")