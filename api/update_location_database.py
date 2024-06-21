import os
from geopy.geocoders import Nominatim

from utils import *


def get_location(location: str) -> str:
    """Get coords of location text from Nominatim geocoder

    :param str location: text for one location in UK.
    :return str: coords lat,lon
    """
    geolocator = Nominatim(user_agent="my_geocoder")
    location = f"{location.strip()}, UK"
    coords = geolocator.geocode(location)
    return (
        DEFAULT_LOCATION if coords is None else f"{coords.latitude},{coords.longitude}"
    )


def update_location_database(location_colname: str = "location_clean") -> str:
    """Update location database. Fetches locations from all users, gets coords of all locations that don't exist in database, and writes to Google Sheets.

    :param str location_colname: column name of user locations, defaults to "location_clean"
    :return str: spreadsheet write status message.
    """
    spreadsheet = get_spreadsheet()
    records = read_spreadsheet(spreadsheet, sheet=os.getenv("RECORDS_SHEET"))
    locations = read_spreadsheet(spreadsheet, sheet="locations")

    print("EXISTING LOCATIONS", [loc["location"] for loc in locations])

    user_locations = set(
        sum([split_location_text(record[location_colname]) for record in records], [])
    )

    new_locations = []
    for location in user_locations:
        if location not in [
            loc["location"] for loc in locations
        ]:  # dynamically update locations
            print("NEW LOCATION:", location)
            coords = get_location(location)
            locations += [{"location": location, "latlon": coords}]
            new_locations += [[location, coords]]

    print(new_locations)

    return write_spreadsheet(new_locations, spreadsheet, "locations")


if __name__ == "__main__":
    update_location_database(location_colname=os.getenv("LOCATION_PROMPT"))
