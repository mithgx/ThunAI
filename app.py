import streamlit as st
import googlemaps
import folium
from streamlit_folium import folium_static
from streamlit_js_eval import get_geolocation
from twilio.rest import Client
from datetime import datetime
import pickle
import pandas as pd

# Load the trained model for risk level prediction
model = pickle.load(open("location_risk_model.pkl", "rb"))


# Function to predict the risk level of a location
def predict_risk_level(latitude, longitude, population_density, crime_rate, past_incidents):
    input_data = [[latitude, longitude, population_density, crime_rate, past_incidents]]
    prediction = model.predict(input_data)[0]  # Predict risk level
    return prediction

# Twilio credentials
TWILIO_ACCOUNT_SID = 'ACc5ad25b1e6929661204f8d07e872837a'
TWILIO_AUTH_TOKEN = '892ca5f2899fec731298d7dbdde9109c'
TWILIO_PHONE_NUMBER = '+18106571943'
POLICE_CONTACT_NUMBER = '+919150980404'

# Set your Google Maps API key
YOUR_GOOGLE_MAPS_API_KEY = 'AIzaSyBNhs7f0N7qUZgp6S5By6aPrRQuphq3I_Y'
gmaps = googlemaps.Client(key=YOUR_GOOGLE_MAPS_API_KEY)

# Local storage for incidents and forum messages
incidents_list = []
forum_messages = []

# Emergency alert function
def send_emergency_message(emergency_contact, lat, lng):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    google_maps_link = f"https://www.google.com/maps?q={lat},{lng}"
    emergency_message = f"This is an emergency! Help needed at: {google_maps_link}"
    
    try:
        formatted_emergency_contact = f"+91{emergency_contact}"
        client.messages.create(body=emergency_message, from_=TWILIO_PHONE_NUMBER, to=formatted_emergency_contact)
        client.messages.create(body=emergency_message, from_=TWILIO_PHONE_NUMBER, to=POLICE_CONTACT_NUMBER)
        st.success("Emergency message with location sent!")
    except Exception as e:
        st.error(f"Failed to send emergency message: {e}")

# Get location name from coordinates
def get_location_name(lat, lng):
    try:
        result = gmaps.reverse_geocode((lat, lng))
        return result[0]['formatted_address']
    except Exception as e:
        st.error(f"Error fetching location data: {e}")
        return "Error fetching location"

# Search location by name
def search_location(location_name):
    try:
        geocode_result = gmaps.geocode(location_name)
        if geocode_result:
            loc = geocode_result[0]['geometry']['location']
            return loc['lat'], loc['lng'], location_name
        return None, None, "Location not found"
    except Exception as e:
        st.error(f"Error searching for location: {e}")
        return None, None, "Error searching for location"

# Incident reporting
def report_incident(location_name, lat, lng, description):
    incident_data = {
        'location_name': location_name, 
        'latitude': lat, 
        'longitude': lng, 
        'description': description, 
        'timestamp': datetime.now()
    }
    incidents_list.append(incident_data)

# Fetch incidents
def fetch_incidents():
    return incidents_list

# Forum Functions
def post_message(username, message):
    forum_data = {
        'username': username,
        'message': message,
        'timestamp': datetime.now()
    }
    forum_messages.append(forum_data)

def fetch_forum_messages():
    return forum_messages

# Function to find nearby places
def find_nearby_places(lat, lng, place_type):
    try:
        place_type_mapping = {
            "Police Station": "police",
            "Bus Stop": "bus_station"
        }
        
        selected_place_type = place_type_mapping.get(place_type)

        if selected_place_type:
            places_result = gmaps.places_nearby(location=(lat, lng), radius=5000, type=selected_place_type)
            return [{'name': place['name'], 'latitude': place['geometry']['location']['lat'], 'longitude': place['geometry']['location']['lng']} for place in places_result['results']]
        else:
            st.error("Invalid place type selected.")
            return []
    except Exception as e:
        st.error(f"Error fetching nearby places: {e}")
        return []
    
    

# App layout
st.title("ThunAI")

# Create tabs
tab1, tab2 = st.tabs(["Home", "Forum"])

# Home Tab
with tab1:
    loc = get_geolocation()
    if loc:
        lat = loc['coords']['latitude']
        lng = loc['coords']['longitude']
        location_name = get_location_name(lat, lng)

        emergency_contact = st.text_input("Enter your emergency contact number", max_chars=10, help="Enter the number without +91")
        
        if st.button("Send Emergency Alert"):
            if emergency_contact:
                send_emergency_message(emergency_contact, lat, lng)
            else:
                st.warning("Please enter a valid emergency contact number.")
        
        st.subheader("Find Nearby Places")
        place_type = st.selectbox("Select Type:", ("Police Station", "Bus Stop"))
        
        if st.button("Search Nearby"):
            nearby_places = find_nearby_places(lat, lng, place_type)
            if nearby_places:
                st.success(f"Found {len(nearby_places)} nearby {place_type.lower()}(s):")
                for place in nearby_places:
                    st.write(f"{place['name']}")
            else:
                st.warning("No nearby places found.")

        if lat and lng:
            st.write(f"Location: **{location_name}**")
            m = folium.Map(location=[lat, lng], zoom_start=12)
            folium.Marker(location=[lat, lng], popup=f"Your Location: {location_name}", icon=folium.Icon(color='blue')).add_to(m)
            
            for incident in fetch_incidents():
                folium.Marker(
                    location=[incident['latitude'], incident['longitude']],
                    popup=f"Incident: {incident['description']}<br>Location: {incident['location_name']}",
                    icon=folium.Icon(color='red')
                ).add_to(m)
            
            folium_static(m)
            

        st.subheader("Report an Incident")
        report_location = st.text_input("Enter Location for Incident (leave blank for current location):", value=location_name)
        description = st.text_area("Incident Description", placeholder="Describe what happened...", key="incident_description")
        
        if st.button("Submit Incident"):
            if description:
                reported_lat, reported_lng, reported_location_name = search_location(report_location) if report_location else (lat, lng, location_name)
                report_incident(reported_location_name, reported_lat, reported_lng, description)
                st.success("Incident reported successfully!")
            else:
                st.error("Please provide a description of the incident.")
    else:
        st.warning("Unable to get your location. Please make sure you've granted location access.")

# Forum Tab
if 'forum_messages' not in st.session_state:
    # Sample data
    st.session_state.forum_messages = pd.DataFrame({
        'username': ["Rahul", "Anjali", "Meera", "Ramesh", "Kavya"],
        'message': [
            "I just saw a group of people acting suspiciously near the railway station. Stay cautious if you're nearby!",
            "The streetlights near XYZ Park are not working. It feels unsafe at night. Anyone else noticed this?",
            "Someone tried to snatch my bag near the bus stop. Please be careful and hold your belongings tightly.",
            "If you're traveling late at night, try to stick to well-lit roads and use public transport when possible.",
            "Does anyone know if there are enough police patrols in this area? I feel it's a bit deserted at night."
        ],
        'category': ["Emergency Alert", "Infrastructure", "Emergency Alert", "Safety Tip", "General"],
        'timestamp': [datetime.now() for _ in range(5)],
        'upvotes': [5, 3, 7, 2, 0],
        'location': ["Railway Station", "XYZ Park", "Bus Stop", "City Center", "Residential Area"],
        'urgency': ["High", "Medium", "High", "Low", "Medium"],
        'is_verified': [True, False, True, False, False]
    })

# Function to extract location from text using simple pattern matching
def extract_location(text):
    # Simple regex-based location extraction
    locations = ["railway station", "park", "bus stop", "mall", "market", "school", 
                "college", "hospital", "temple", "mosque", "church", "bridge", "highway"]
    
    text_lower = text.lower()
    
    for loc in locations:
        if loc in text_lower:
            return loc.title()
    
    return "Unspecified Location"

# Function to estimate message urgency based on keywords
def estimate_urgency(message):
    # Simple keyword-based urgency detection
    high_urgency_keywords = ["emergency", "danger", "attack", "threat", "assault", 
                           "robbery", "fire", "accident", "weapon", "suspicious"]
    medium_urgency_keywords = ["cautious", "unsafe", "crime", "dark", "broken", 
                             "warning", "attention", "careful"]
    
    message_lower = message.lower()
    
    # Check for high urgency keywords
    for keyword in high_urgency_keywords:
        if keyword in message_lower:
            return "High"
    
    # Check for medium urgency keywords
    for keyword in medium_urgency_keywords:
        if keyword in message_lower:
            return "Medium"
    
    # Default to low urgency
    return "Low"

# Function to post a message
def post_message(username, message, category, location):
    # Estimate urgency
    urgency = estimate_urgency(message)
    
    # Add new message to the dataframe
    new_message = {
        'username': username if username else "Anonymous",
        'message': message,
        'category': category,
        'timestamp': datetime.now(),
        'upvotes': 0,
        'location': location,
        'urgency': urgency,
        'is_verified': False  # New messages start unverified
    }
    
    st.session_state.forum_messages = pd.concat([
        st.session_state.forum_messages, 
        pd.DataFrame([new_message])
    ], ignore_index=True)
    
    return True

# Function to display messages with enhanced formatting
def display_messages(filtered_messages):
    if len(filtered_messages) == 0:
        st.warning("No messages found.")
        return
    
    # Sort messages by urgency, timestamp, and upvotes
    sorted_messages = filtered_messages.sort_values(
        by=['urgency', 'timestamp', 'upvotes'], 
        ascending=[False, False, False]
    )
    
    for idx, msg in sorted_messages.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            # Determine card color based on urgency
            urgency_indicator = {
                "High": "🔴", 
                "Medium": "🟠", 
                "Low": "🟢"
            }.get(msg['urgency'], "🟢")
            
            # Format header with username, timestamp, category
            header = f"{urgency_indicator} **{msg['username']}** "
            if msg['is_verified']:
                header += "✓ "
            
            header += f"| 🕒 {msg['timestamp'].strftime('%Y-%m-%d %H:%M')} | 🏷️ {msg['category']}"
            
            with col1:
                st.markdown(header)
                
                # Message content
                message_box = {
                    "High": st.error,
                    "Medium": st.warning,
                    "Low": st.info
                }.get(msg['urgency'], st.info)
                
                message_box(msg['message'])
                
                # Location info
                st.caption(f"📍 {msg['location']}")
            
            with col2:
                # Upvote button and count
                if st.button(f"👍 {msg['upvotes']}", key=f"upvote_{idx}"):
                    st.session_state.forum_messages.at[idx, 'upvotes'] += 1
                    st.experimental_rerun()
                
                # Verify button (could be limited to admins in a real app)
                if not msg['is_verified']:
                    if st.button("✓ Verify", key=f"verify_{idx}"):
                        st.session_state.forum_messages.at[idx, 'is_verified'] = True
                        st.experimental_rerun()
            
            st.markdown("---")

# Main Forum UI
def forum_tab():
    st.title("🗣️ Community Safety Forum")
    st.write("Share safety concerns and incidents with the community.")
    
    # Basic stats
    if len(st.session_state.forum_messages) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Posts", len(st.session_state.forum_messages))
        with col2:
            high_urgency = len(st.session_state.forum_messages[st.session_state.forum_messages['urgency'] == "High"])
            st.metric("High Urgency", high_urgency)
        with col3:
            verified = len(st.session_state.forum_messages[st.session_state.forum_messages['is_verified']])
            st.metric("Verified Posts", verified)
    
    # Tabs for different forum views
    post_tab, browse_tab = st.tabs(["Post Message", "Browse Messages"])
    
    # Post Message Tab
    with post_tab:
        st.subheader("Share Your Message")
        
        # Message input form
        username = st.text_input("Your Name (or leave blank for anonymous)", key="forum_username")
        
        # Category selection with explanations
        category_options = {
            "Emergency Alert": "Immediate safety concerns that require attention",
            "Infrastructure": "Issues with roads, lights, or public facilities",
            "Suspicious Activity": "Unusual behavior that might indicate criminal intent",
            "Crime Report": "Reports of crimes that have occurred",
            "Safety Tip": "Advice to help others stay safe",
            "General": "Other safety-related discussions"
        }
        
        category = st.selectbox(
            "Category",
            options=list(category_options.keys()),
            format_func=lambda x: f"{x} - {category_options[x]}"
        )
        
        # Message input with placeholder based on category
        placeholders = {
            "Emergency Alert": "Describe the emergency situation in detail...",
            "Infrastructure": "Describe the infrastructure issue and its location...",
            "Suspicious Activity": "Describe what you saw and why it seemed suspicious...",
            "Crime Report": "Describe the incident that occurred (no personal details)...",
            "Safety Tip": "Share your safety advice or recommendation...",
            "General": "Type your message here..."
        }
        
        message = st.text_area(
            "Your Message", 
            height=150,
            placeholder=placeholders.get(category, "Type your message here...")
        )
        
        # Location input with automatic extraction
        if message:
            extracted_location = extract_location(message)
            location = st.text_input(
                "Location",
                value=extracted_location if extracted_location != "Unspecified Location" else "",
                placeholder="Where did this occur? (automatically detected when possible)"
            )
        else:
            location = st.text_input(
                "Location",
                placeholder="Where did this occur?"
            )
        
        # Submit button
        if st.button("Post Message", type="primary"):
            if message:
                if post_message(username, message, category, location):
                    st.success("Message posted successfully!")
                    # Add automatic switching to browse tab
                    st.experimental_rerun()
            else:
                st.error("Please enter a message to post.")
    
    # Browse Messages Tab
    with browse_tab:
        st.subheader("Community Messages")
        
        # Filter controls
        with st.expander("Filter Options", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Filter by category
                selected_categories = st.multiselect(
                    "Filter by Category",
                    options=st.session_state.forum_messages['category'].unique()
                )
                
                # Filter by location
                selected_locations = st.multiselect(
                    "Filter by Location",
                    options=st.session_state.forum_messages['location'].unique()
                )
            
            with col2:
                # Filter by urgency
                selected_urgencies = st.multiselect(
                    "Filter by Urgency Level",
                    options=["High", "Medium", "Low"]
                )
                
                # Filter by verification status
                verification_status = st.radio(
                    "Verification Status",
                    options=["All", "Verified Only", "Unverified Only"]
                )
        
        # Search functionality
        search_query = st.text_input("🔍 Search Messages", placeholder="Enter keywords...")
        
        # Apply filters
        filtered_df = st.session_state.forum_messages.copy()
        
        # Category filter
        if selected_categories:
            filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
        
        # Location filter
        if selected_locations:
            filtered_df = filtered_df[filtered_df['location'].isin(selected_locations)]
        
        # Urgency filter
        if selected_urgencies:
            filtered_df = filtered_df[filtered_df['urgency'].isin(selected_urgencies)]
        
        # Verification status filter
        if verification_status == "Verified Only":
            filtered_df = filtered_df[filtered_df['is_verified']]
        elif verification_status == "Unverified Only":
            filtered_df = filtered_df[~filtered_df['is_verified']]
        
        # Search filter
        if search_query:
            # Simple search
            search_query = search_query.lower()
            filtered_df = filtered_df[
                filtered_df['message'].str.lower().str.contains(search_query) | 
                filtered_df['username'].str.lower().str.contains(search_query) |
                filtered_df['location'].str.lower().str.contains(search_query)
            ]
        
        # Sort options
        sort_by = st.selectbox(
            "Sort by",
            options=["Most Urgent", "Most Recent", "Most Upvoted"],
            index=0
        )
        
        if sort_by == "Most Recent":
            filtered_df = filtered_df.sort_values('timestamp', ascending=False)
        elif sort_by == "Most Upvoted":
            filtered_df = filtered_df.sort_values('upvotes', ascending=False)
        # "Most Urgent" is the default in display_messages
        
        # Display filtered messages
        st.write(f"Showing {len(filtered_df)} messages")
        display_messages(filtered_df)

# Call the forum tab function to display in the app
forum_tab()