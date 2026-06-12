import streamlit as st
import requests
import xml.etree.ElementTree as ET

# Set up the app page (Changes the browser tab / home screen name)
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

def get_cheapest_fuel(suburb="Midland", product=1):
    url = f"https://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?Product={product}&Suburb={suburb}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
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
        
    # Sort to find the absolute lowest price
    stations.sort(key=lambda x: x['price'])
    return stations[0]

# --- App UI ---
# Changes the big header text on the page itself
st.title("Moyo's Cheap Fuel Finder ⛽")
st.write("Find the lowest fuel prices around the Midland area right now.")

# The dropdown menu
selected_fuel_name = st.selectbox("Select your fuel type:", list(FUEL_TYPES.keys()))
selected_fuel_code = FUEL_TYPES[selected_fuel_name]

# The button updates dynamically based on what you choose
if st.button(f"Find Cheapest {selected_fuel_name}"):
    with st.spinner(f"Searching for {selected_fuel_name}..."):
        cheapest = get_cheapest_fuel("Midland", selected_fuel_code)
        
        if cheapest:
            st.success(f"**{cheapest['price']} c/L** at **{cheapest['name']}**")
            st.write(f"📍 {cheapest['address']}, {cheapest['suburb']}")
            
            # Create a direct Google Maps pin using the exact latitude and longitude
            maps_url = f"https://www.google.com/maps/search/?api=1&query={cheapest['lat']},{cheapest['lon']}"
            st.link_button("🗺️ Open in Google Maps", maps_url)
        else:
            st.error(f"Couldn't find any {selected_fuel_name} data for Midland right now. Try again later.")
