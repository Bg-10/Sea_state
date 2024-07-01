import openmeteo_requests
import streamlit as st
import requests_cache
import pandas as pd
from retry_requests import retry
st.title("How's my sea looking? :sun_behind_rain_cloud:")

st.subheader("Choose location")
st.markdown('[Click Here to choose Location Coordinates from Google Maps](https://www.google.com/maps/@11.0247763,59.0872192,5z?entry=ttu)')

lat = st.text_input("Enter Latitude")
lng = st.text_input("Enter Longitude")
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
# Make sure all required weather variables are listed here
url = "https://marine-api.open-meteo.com/v1/marine"

params = {
	"latitude": lat,
	"longitude": lng,
	"current": ["wave_height", "wave_period", "ocean_current_velocity", "ocean_current_direction"]
}
responses = openmeteo.weather_api(url, params=params)
st.subheader("Current Ocean Parameters:")
response = responses[0]
st.info(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
st.info(f"Elevation {response.Elevation()} m asl")
# st.info(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
# st.info(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_wave_height = current.Variables(0).Value()
current_wave_period = current.Variables(1).Value()
current_ocean_current_velocity = current.Variables(2).Value()
current_ocean_current_direction = current.Variables(3).Value()

st.info(f"Current time {current.Time()}")
st.info(f"Current wave_height {current_wave_height}")
st.info(f"Current wave_period {current_wave_period}")
st.info(f"Current ocean_current_velocity {current_ocean_current_velocity}")
st.info(f"Current ocean_current_direction {current_ocean_current_direction}")

# create model to return sea state using the above time period and wave height parameters 
# Beaufort Scale
st.title("Sea State")
st.info(f"Sea conditions are classified on a scale of 1 to 9 according to WMO, 1 being calm sea and 9 being hurricane conditions.")

class SeaStateClassifier:
    def __init__(self, current_wave_height):
        self.current_wave_height = current_wave_height

    def classify_sea_state(self):
        if self.current_wave_height <= 0.3:
            return "Sea state 1 condition: Calm (rippled sea with no crests)"
        elif 0.3 < self.current_wave_height <= 0.6:
            return "Sea state 2 condition: Small Wavelets and glassy crests"
        elif 0.6 < self.current_wave_height <= 1.2:
            return "Sea state 3 condition: Large wavelets with crest breaking"
        elif 1.2 < self.current_wave_height <= 2:
            return "Sea state 4 condition: Long waves and frequent white horses"
        elif 2 < self.current_wave_height <= 3:
            return "Sea state 5 condition: Crested wavelets in inland waters"
        elif 3 < self.current_wave_height <= 4:
            return "Sea state 6 condition: Large waves, crests, and spray"
        elif 4 < self.current_wave_height <= 5.5:
            return "Sea state 7 condition: Moderate gale"
        elif 5.5 < self.current_wave_height <=7.5:
            return "Sea State 8 condition: dense foam, reduced visibility, gale"
        elif 7.5<self.current_wave_height<=14:
            return "Sea state 9 condition : strong Gale with sprays and low visibility"
        elif self.current_wave_height > 14:
            return "Sea state 10 condition: Violent storm with Serios visibility affected"

classifier = SeaStateClassifier(current_wave_height)
sea_state_info = classifier.classify_sea_state()
st.info(sea_state_info)
