from geopy.geocoders import Nominatim

# Initialize the geocoder
geolocator = Nominatim(user_agent="my_geocoder")

# Example: Geocode an address
location = geolocator.geocode("london, UK")
print("Latitude and Longitude:", (location.latitude, location.longitude))