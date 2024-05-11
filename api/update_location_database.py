from utils import *
from geopy.geocoders import Nominatim

def get_location(location) -> str:
    geolocator = Nominatim(user_agent="my_geocoder")
    location = f"{location.strip()}, UK"
    coords = geolocator.geocode(location)
    return "0,0" if coords is None else f"{coords.latitude},{coords.longitude}"

def update_location_database(location_colname="location_clean"):
    spreadsheet = get_spreadsheet()
    records = read_spreadsheet(spreadsheet, sheet=os.getenv("RECORDS_SHEET"))
    locations = read_spreadsheet(spreadsheet, sheet="locations")

    print("EXISTING LOCAITONS")
    print([loc["location"] for loc in locations])

    user_locations = set(sum([split_location_text(record[location_colname]) for record in records], []))

    new_locations = []
    for location in user_locations:
        if location not in [loc["location"] for loc in locations]:
            print("NEW LOCATION:", location)
            coords = get_location(location)
            locations += [{"location": location, "latlon": coords}]
            new_locations += [location, coords]

    status = write_spreadsheet(new_locations, spreadsheet, "locations")
    return status

if __name__ == "__main__":
    update_location_database(
        location_colname="Location (optional, to be added anonymously to the ESEA map)"
    )