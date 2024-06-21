import os, json, re
from collections import defaultdict
from enum import Enum
from typing import List, Dict

from dotenv import load_dotenv
from google.oauth2 import service_account
import gspread

load_dotenv()

AUTH_LEVEL = Enum("AUTH_LEVEL", ["PUBLIC", "MEMBERS", "DEV", "DENIED"])
DEFAULT_LOCATION = "10,10"


def get_spreadsheet() -> gspread.Spreadsheet:
    """Open Google Sheet defined by URL and credentials from environment variables

    :return gspread.Spreadsheet: Google Sheets object
    """
    client = gspread.authorize(
        service_account.Credentials.from_service_account_info(
            json.loads(os.getenv("GOOGLE_JSON"))
        ).with_scopes(
            [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
        )
    )
    return client.open_by_url(os.getenv("GOOGLE_SPREADSHEET"))


def read_spreadsheet(
    spreadsheet: gspread.Spreadsheet, sheet: str = "Sheet1"
) -> List[Dict]:
    """Read Google Sheet and return list of rows

    :param gspread.Spreadsheet spreadsheet: Google Sheets object
    :param str sheet: name of sheet, defaults to "Sheet1"
    :return list[dict]: list of dicts, where each dict is a row containing col:value
    """
    return spreadsheet.worksheet(sheet).get_all_records()


def write_spreadsheet(
    rows: List[List], spreadsheet: gspread.Spreadsheet, sheet: str = "Sheet1"
) -> str:
    """Write list of rows to Google Sheet.

    :param list rows: list of rows, where each row is a list of cells, NOT a dict
    :param gspread.Spreadsheet spreadsheet: Google Sheets object
    :param str sheet: name of sheet, defaults to "Sheet1"
    :return str: spreadsheet write status message.
    """
    if len(rows) > 0:
        spreadsheet.worksheet(sheet).append_rows(rows)

    status = f"Written {len(rows)} rows to sheet: {sheet}"
    print(status)
    return status


def get_users_from_records(
    records: List[Dict],
    locations: List[Dict],
    auth_level: AUTH_LEVEL = AUTH_LEVEL.PUBLIC,
) -> List[Dict]:
    """Get clean list of users from records from Google Sheets.

    :param List[Dict] records: records from main sheet containing all user info
    :param List[Dict] locations: records from location sheet containing user location info
    :param AUTH_LEVEL auth_level: auth level for how much info to return, defaults to AUTH_LEVEL.PUBLIC
    :return List[Dict]: list of users where each user is a dict with keys "name", "locations", "phone"
    """
    location_dict = defaultdict(
        lambda: DEFAULT_LOCATION, {loc["location"]: loc["latlon"] for loc in locations}
    )

    print(records)

    return [
        {
            "name": redact_name(
                record["firstName"],
                record["lastName"],
                auth_level=auth_level,
                filter1=0,
                filter2=3,
            ),  # filter1=int(record["map1"]), filter2=int(record["map2"])),
            "locations": [
                {"name": location.title(), "coords": location_dict[location]}
                for location in split_location_text(
                    record[os.getenv("LOCATION_PROMPT")]
                )
            ],
            "phone": redact_phone(
                record.get("number_clean", ""),
                auth_level=auth_level,
                filter1=0,
                filter2=3,
            ),  # filter1=int(record["map1"]), filter2=int(record["map2"])),
        }
        for record in records  # if record["wa"] == "TRUE" #and int(record["map1"]) != -1 and int(record["map2"])) != -1
    ]


def split_location_text(location_text: str, sep: str = "/") -> List[str]:
    """Split and clean location text into list of clean locations to be matched and/or geocoded.

    :param str location_text: location text e.g. "Edinburgh" or "Manchester/London"
    :param str sep: separator, defaults to "/"
    :return List[str]: list of clean locations
    """

    def clean(loc: str) -> str:
        loc = re.sub(r'\(.*?\)', '', loc) # remove brackets and text inside
        loc = loc.strip().lower()
        loc = "" if loc in ["no", "none"] else loc
        return loc

    # Replace "and" with sep
    location_text_clean = re.sub(r'\band\b', sep, location_text, flags=re.IGNORECASE)

    locations = [clean(location) for location in location_text_clean.replace(";", sep).split(sep)]

    if "Sheffield" in location_text:
        print(locations)
    return [location for location in locations if location]


def redact_phone(
    phone: str,
    auth_level: AUTH_LEVEL = AUTH_LEVEL.PUBLIC,
    filter1: int = 0,
    filter2: int = 0,
) -> str:
    """Redact phone number according to auth_level and filters.

    :param str phone: phone number from user records.
    :param AUTH_LEVEL auth_level: auth level for how much detail to return, defaults to AUTH_LEVEL.PUBLIC
    :param int filter1: filter, see ESEAOUK Form Responses spreadsheet for more details, defaults to 0
    :param int filter2: filter, see ESEAOUK Form Responses spreadsheet for more details, defaults to 0
    :raises ValueError: invalid auth level
    :return str: redacted phone number
    """
    phone = str(phone).strip()

    if phone == "" or phone is None:
        return ""
    elif auth_level in (AUTH_LEVEL.PUBLIC, AUTH_LEVEL.DENIED):
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


def redact_name(
    first_name: str,
    last_name: str,
    auth_level: AUTH_LEVEL = AUTH_LEVEL.PUBLIC,
    filter1: int = 0,
    filter2: int = 0,
) -> str:
    """Build name and redact name according to auth_level and filters.

    :param str first_name: firt name
    :param str last_name: last name
    :param AUTH_LEVEL auth_level: auth level for how much detail to return, defaults to AUTH_LEVEL.PUBLIC
    :param int filter1: filter, see ESEAOUK Form Responses spreadsheet for more details, defaults to 0
    :param int filter2: filter, see ESEAOUK Form Responses spreadsheet for more details, defaults to 0
    :raises ValueError: invalid auth level
    :return str: redacted name
    """

    first_name = str(first_name).strip()
    last_name = str(last_name).strip()
    name = f"{first_name} {last_name}"

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
