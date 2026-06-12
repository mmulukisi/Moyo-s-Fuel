import streamlit as st
import requests
import xml.etree.ElementTree as ET
import urllib.parse
from streamlit_js_eval import get_geolocation

# Set up the app page
st.set_page_config(page_title="Moyo's Cheap Fuel Finder", page_icon="⛽")

# The official FuelWatch WA codes for every fuel type
FUEL_TYPES = {
    "Unleaded Petrol (ULP)": 1,
    "Premium Unleaded (95)": 2,
    "Premium 98 (RON)": 6,
    "Diesel": 4,
    "Brand Diesel": 11,
    "LPG": 5,
    "E85": 10
}

def get_suburb_from_coords(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14&addressdetails=1"
    headers = {'User-Agent': 'MoyosFuelApp/1.0'}
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        address = data.get("address", {})
        return address.get("suburb") or address.get("town") or address.get("village") or address.get("city")
    except Exception:
        return None

def get_cheapest_fuel(suburb, product=1):
    safe_suburb = urllib.parse.quote(suburb.strip())
    url = f"https://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?Product={product}&Suburb={safe_suburb}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        root = ET.fromstring(response.content)
    except Exception:
        return None
        
    stations = []
    for item in root.findall('./channel/item'):
        try:
            stations.append({
                'price': float(item.find('price').text),
                'name': item.find('trading-name').text,
                'address': item.find('address').text,
                'suburb': item.find('location').text,
                'lat': item.find('latitude').text,
                'lon': item.find('longitude').text
            })
        except AttributeError:
            continue
        
    if not stations:
        return None
        
    stations.sort(key=lambda x: x['price'])
    return stations[0]

# --- App UI ---
st.title("Moyo's Cheap Fuel Finder ⛽")
st.write("Find the lowest fuel prices nearby.")

loc = get_geolocation()

if loc:
    if 'error' in loc:
        st.error("Location access denied. Please type a suburb below.")
        auto_suburb = "Midland"
    else:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        auto_suburb = get_suburb_from_coords(lat, lon) or "Midland"
        st.success(f"📍 Location: {auto_suburb.title()}")
else:
    st.info("Waiting for GPS... (Tap 'Allow' if prompted)")
    auto_suburb = "Midland"

selected_suburb = st.text_input("Suburb:", value=auto_suburb)
selected_fuel_name = st.selectbox("Fuel type:", list(FUEL_TYPES.keys()))
selected_fuel_code = FUEL_TYPES[selected_fuel_name]

if st.button("Find Cheapest Fuel"):
    if not selected_suburb:
        st.warning("Please enter a suburb!")
    else:
        with st.spinner("Searching..."):
            cheapest = get_cheapest_fuel(selected_suburb, selected_fuel_code)
            if cheapest:
                st.success(f"**{cheapest['price']} c/L** at {cheapest['name']}")
                st.write(f"📍 {cheapest['address']}, {cheapest['suburb']}")
                maps_url = f"https://www.google.com/maps/search/?api=1&query={cheapest['lat']},{cheapest['lon']}"
                st.link_button("🗺️ Open in Google Maps", maps_url)
            else:
                st.error("No data found. Try a nearby suburb.")
