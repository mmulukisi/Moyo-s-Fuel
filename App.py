import streamlit as st
import requests
import xml.etree.ElementTree as ET

# Set up the app page
st.set_page_config(page_title="Moyo's Fuel", page_icon="⛽")

def get_cheapest_fuel(suburb="Midland", product=1):
    # Product 1 is Unleaded Petrol (ULP). 
    url = f"https://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?Product={product}&Suburb={suburb}"
    
    try:
        response = requests.get(url)
        root = ET.fromstring(response.content)
    except Exception:
        return None
        
    stations = []
    
    # FuelWatch RSS puts data inside <channel><item>
    for item in root.findall('./channel/item'):
        stations.append({
            'price': float(item.find('price').text),
            'name': item.find('trading-name').text,
            'address': item.find('address').text,
            'suburb': item.find('location').text,
            'lat': item.find('latitude').text,
            'lon': item.find('longitude').text
        })
        
    if not stations:
        return None
        
    # Sort to find the absolute lowest price
    stations.sort(key=lambda x: x['price'])
    return stations[0]

# --- App UI ---
st.title("Moyo's Fuel ⛽")
st.write("Find the lowest Unleaded (ULP) prices around the Midland area right now.")

# The magic button
if st.button("Find Cheapest Fuel"):
    with st.spinner("Checking FuelWatch WA..."):
        cheapest = get_cheapest_fuel("Midland")
        
        if cheapest:
            st.success(f"**{cheapest['price']} c/L** at **{cheapest['name']}**")
            st.write(f"📍 {cheapest['address']}, {cheapest['suburb']}")
            
            # Create a direct Google Maps pin using the exact latitude and longitude
            maps_url = f"https://www.google.com/maps/search/?api=1&query={cheapest['lat']},{cheapest['lon']}"
            
            # The push-button routing you asked for
            st.link_button("🗺️ Open in Google Maps", maps_url)
        else:
            st.error("Couldn't find any fuel data. Try again later.")
