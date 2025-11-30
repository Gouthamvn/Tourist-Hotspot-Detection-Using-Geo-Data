import streamlit as st
import pandas as pd
import pymongo
import openai
import webbrowser
import hashlib
import plotly.express as px
from streamlit_option_menu import option_menu
import time

# ===== Page Configurations =====
st.set_page_config(page_title="🌍 Tourist HotSpot Finder", layout="wide")

# ===== MongoDB Setup =====
try:
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["tourism_db"]
    places_collection = db["places"]
    users_collection = db["users"]
    client.server_info()
except pymongo.errors.ConnectionFailure as e:
    st.error(f"Could not connect to MongoDB. Please ensure it's running. Error: {e}")
    st.stop()

# ===== Load Dataset =====
@st.cache_data
def load_dataset():
    DATA_PATH = "updated_tourist_places_dataset.csv"
    try:
        df = pd.read_csv(DATA_PATH)
        # Remove rows with missing critical fields
        df = df.dropna(subset=["Country", "State", "City", "Tourist Place"])
        return df
    except FileNotFoundError:
        st.error(f"Dataset file not found at {DATA_PATH}. Please check the file path.")
        return pd.DataFrame()

# ===== OpenAI API Key for Chatbot =====
OPENAI_API_KEY = "your-openai-api-key"
openai.api_key = OPENAI_API_KEY

# ===== User Authentication Functions =====
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# ===== Custom CSS Styling =====
def local_css():
    st.markdown("""
        <style>
        /* ===== Main App Background (after login) ===== */
        .main-app-container {
            background: linear-gradient(135deg, rgba(173, 216, 230, 0.7) 0%, rgba(255, 192, 203, 0.7) 100%);
            background-size: cover;
        }

        /* ===== Login/Signup Background with Running Shadow Effect ===== */
        .login-background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
        }
        
        @keyframes gradient {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        
        /* ===== Form Container ===== */
        .form-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin: 2rem auto;
            max-width: 500px;
        }

        /* ===== Title Styling ===== */
        .main-title {
            text-align: center;
            font-size: 3rem;
            font-weight: 800;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5),
                        -1px -1px 0 #000,  
                        1px -1px 0 #000,
                        -1px 1px 0 #000,
                        1px 1px 0 #000;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            text-align: center;
            color: white;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }

        /* ===== Input Fields ===== */
        .stTextInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.9);
            color: #1F2937;
            border-radius: 10px;
            border: 1px solid #CBD5E1;
            padding: 10px 14px;
            transition: all 0.2s ease;
        }
        .stTextInput > div > div > input:focus {
            border: 1px solid #3B82F6;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.2);
            outline: none;
        }

        /* ===== Button Styling ===== */
        .stButton > button {
            width: 100%;
            border-radius: 10px;
            background-color: #3B82F6;
            color: white;
            font-weight: 600;
            border: none;
            padding: 10px 14px;
            cursor: pointer;
            transition: all 0.25s ease;
        }
        .stButton > button:hover {
            background-color: #2563EB;
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }

        /* ===== Radio Button Styling ===== */
        .stRadio > div {
            flex-direction: row;
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        .stRadio > div > label {
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stRadio > div > label:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        /* ===== Home Page Image Styling ===== */
        .image-container {
            position: relative;
            text-align: center;
            width: 100%;
        }
        .centered-title {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 40px;
            font-weight: 600;
            color: #1E293B;
            background: rgba(255, 255, 255, 0.85);
            padding: 14px 24px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transition: all 0.25s ease;
        }
        .centered-title:hover {
            background: #F1F5F9;
            transform: translate(-50%, -50%) scale(1.02);
            box-shadow: 0 6px 14px rgba(0,0,0,0.15);
        }
        
        /* ===== Main Content Styling ===== */
        .main .block-container {
            background: linear-gradient(135deg, rgba(173, 216, 230, 0.7) 0%, rgba(255, 192, 203, 0.7) 100%);
            padding: 20px;
            border-radius: 15px;
        }
        
        /* ===== Card Styling ===== */
        .card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        /* ==== Background Style for Home Page ==== */
        .stMainBlockContainer{
        background-image: -webkit-linear-gradient(left, #77A1D3 0%, #79CBCA 51%, #77A1D3 100%);

        }
        
        /*====cover Image ====*/
        .image-container{
            background-image: url('./TouristCover.png');

        }
        </style>
    """, unsafe_allow_html=True)

local_css()

# ===== Main Application Logic =====
def main_app():
    # Apply main app background
    st.markdown('<div class="main-app-container">', unsafe_allow_html=True)
    
    # Sidebar Navigation
    with st.sidebar:
        st.write(f"Welcome, {st.session_state['username']}!")
        selected_page = option_menu(
            menu_title="Tourist Explorer",
            options=["🏠 Home", "🔍 Search Places", "📌 Saved Places", "📊 Analysis", "🤖 Chatbot"],
            icons=["house", "search", "bookmark", "bar-chart", "robot"],
            menu_icon="globe",
            default_index=0
        )
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ""
            st.rerun()

    # Home Page
    if selected_page == "🏠 Home":
        image_url = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
        st.markdown(f"""
            <div class="image-container">
                <img src="{image_url}" width="100%">
                <div class="centered-title">🌍 Welcome to Tourist HotSpot Finder</div>
            </div>
        """, unsafe_allow_html=True)
        st.write("### ✈ Explore the best travel destinations around the world.")
        st.write("🌟 Discover amazing places, plan your trips, and make your journey memorable!")

    # Search Places Page
    elif selected_page == "🔍 Search Places":
        st.title("🔍 Search Places")
        df = load_dataset()
        if df.empty: return

        # Initialize session state
        if "search_results" not in st.session_state:
            st.session_state.search_results = pd.DataFrame()
        if "selected_place" not in st.session_state:
            st.session_state.selected_place = None
        if "selected_country" not in st.session_state:
            st.session_state.selected_country = ""
        if "selected_state" not in st.session_state:
            st.session_state.selected_state = ""
        if "selected_city" not in st.session_state:
            st.session_state.selected_city = ""
        if "selected_category" not in st.session_state:
            st.session_state.selected_category = ""

        # Input fields
        countries = df["Country"].dropna().unique().tolist()
        countries = [""] + sorted(countries)
        country = st.selectbox("🌍 Select Country", countries, 
                               index=countries.index(st.session_state.selected_country) if st.session_state.selected_country in countries else 0,
                               key="country_select", help="Choose a country to filter states and cities")
        
        # Reset state and city when country changes
        if country != st.session_state.selected_country:
            st.session_state.selected_country = country
            st.session_state.selected_state = ""
            st.session_state.selected_city = ""

        states = []
        if country:
            states = df[df["Country"] == country]["State"].dropna().unique().tolist()
            states = [""] + sorted(states)
        state = st.selectbox("🏙 Select State", states, 
                             index=states.index(st.session_state.selected_state) if st.session_state.selected_state in states else 0,
                             key="state_select", help="Choose a state to filter cities") if states else None
        if state != st.session_state.selected_state:
            st.session_state.selected_state = state if state else ""
            st.session_state.selected_city = ""  # Reset city when state changes
        if not states and country:
            st.warning("⚠ No states available for the selected country.")

        cities = []
        if state:
            cities = df[(df["Country"] == country) & (df["State"] == state)]["City"].dropna().unique().tolist()
            cities = [""] + sorted(cities)
        city = st.selectbox("🏞 Select City", cities, 
                            index=cities.index(st.session_state.selected_city) if st.session_state.selected_city in cities else 0,
                            key="city_select", help="Choose a city to search for places") if cities else None
        st.session_state.selected_city = city if city else ""
        if not cities and state:
            st.warning("⚠ No cities available for the selected state.")

        category_input = st.text_input("🔎 Search for Place (e.g., beach, museum, park)", 
                                      value=st.session_state.selected_category, 
                                      key="category_input")
        st.session_state.selected_category = category_input

        if st.button("🔍 Search", disabled=not (country and state and city)):
            if country and state and city:
                results = df[(df["Country"] == country) & (df["State"] == state) & (df["City"] == city)]
                if category_input:
                    results = results[results["Tourist Place"].str.contains(category_input, case=False, na=False)]
                st.session_state.search_results = results
                st.session_state.selected_place = None
                if "place_selector" in st.session_state:
                    del st.session_state.place_selector
            else:
                st.warning("⚠ Please select a country, state, and city to search.")

        if st.button("🔄 Reset Search"):
            st.session_state.search_results = pd.DataFrame()
            st.session_state.selected_place = None
            st.session_state.selected_country = ""
            st.session_state.selected_state = ""
            st.session_state.selected_city = ""
            st.session_state.selected_category = ""
            if "place_selector" in st.session_state:
                del st.session_state.place_selector
            st.rerun()

        if not st.session_state.search_results.empty:
            st.success(f"✅ Found {len(st.session_state.search_results)} places in {city}!")
            place_options = st.session_state.search_results["Tourist Place"].tolist()
            selected_place = st.selectbox("📍 Select a Place", place_options, key="place_selector")

            if selected_place and st.session_state.selected_place != selected_place:
                st.session_state.selected_place = selected_place

            if st.session_state.selected_place:
                place_details_df = st.session_state.search_results[st.session_state.search_results["Tourist Place"] == st.session_state.selected_place]
                if not place_details_df.empty:
                    place_details = place_details_df.iloc[0]
                    st.write(f"### Details for {selected_place}")
                    cols = st.columns(2)
                    with cols[0]:
                        st.info(f"🌟 Rating: {place_details.get('Reviews', 'N/A')}")
                        st.info(f"⏳ Recommended Stay: {place_details.get('Recommended Stay', 'N/A')}")
                        st.info(f"📅 Best Time to Visit: {place_details.get('Best Visiting Time', 'N/A')}")
                        st.info(f"👨‍👩‍👧‍👦 Family-Friendly: {place_details.get('Family-Friendly', 'N/A')}")
                    with cols[1]:
                        st.info(f"💰 Entry Fee: {place_details.get('Entry Fee', 'N/A')}")
                        st.info(f"🏕 Adventure Level: {place_details.get('Adventure Level', 'N/A')}")
                        st.info(f"♿ Accessibility: {place_details.get('Accessibility', 'N/A')}")
                    st.info(f"🏨 Nearby Attractions: {place_details.get('Nearby Attractions', 'N/A')}")

                    if st.button("🗺 View in Google Maps"):
                        webbrowser.open(place_details['Google Maps Link'])

                    if st.button("📌 Save Place"):
                        place_dict = place_details.to_dict()
                        place_dict['saved_by'] = st.session_state['username']
                        if not places_collection.find_one({"Tourist Place": place_dict["Tourist Place"], "saved_by": place_dict['saved_by']}):
                            places_collection.insert_one(place_dict)
                            st.markdown(f"""
                                <script>
                                    alert("✅ '{selected_place}' has been successfully saved to your collection!");
                                </script>
                            """, unsafe_allow_html=True)
                            st.success(f"✅ '{selected_place}' has been saved! ")
                            # Wait for 5 seconds to show the success message
                            time.sleep(1)
                            # Reset search results and place selector
                            st.session_state.search_results = pd.DataFrame()
                            st.session_state.selected_place = None
                            if "place_selector" in st.session_state:
                                del st.session_state.place_selector
                            st.rerun()
                        else:
                            st.warning(f"⚠ '{selected_place}' is already saved.")

    # Saved Places Page
    elif selected_page == "📌 Saved Places":
        st.markdown("<h2 style='text-align: center;'>📌 Your Saved Places</h2>", unsafe_allow_html=True)
        saved_places = list(places_collection.find({"saved_by": st.session_state['username']}, {"_id": 0}))
        
        if saved_places:
            st.info(f"You have saved {len(saved_places)} place(s).")
            for place in saved_places:
                delete_key = f"delete_{place['Tourist Place']}_{st.session_state['username']}"
                st.markdown(f"""
                    <div style="border: 2px solid #FFA500; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #FFF3E0;">
                        <h4 style="color: #FF5733;">📍 {place['Tourist Place']}</h4>
                        <p style="color: black;"><b>📍 Location: {place.get('City', 'N/A')}, {place.get('State', 'N/A')}, {place.get('Country', 'N/A')}</b></p>
                        <p style="color: black;"><b>⭐ Reviews: {place.get('Reviews', 'N/A')}</b></p>
                        <p style="color: #000000;"><b>📜 Address: {place.get('Address', 'No Address available')}</b></p>
                        <a href="{place.get('Google Maps Link', '#')}" target="_blank" style="text-decoration: none;">
                            <button style="background-color: #FFA500; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer;">
                                🗺 View on Google Maps
                            </button>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🗑 Delete", key=delete_key):
                    places_collection.delete_one({"Tourist Place": place["Tourist Place"], "saved_by": st.session_state['username']})
                    st.markdown(f"""
                        <script>
                            alert("🗑 '{place['Tourist Place']}' has been successfully deleted from your saved places!");
                        </script>
                    """, unsafe_allow_html=True)
                    st.success(f"🗑 '{place['Tourist Place']}' has been deleted!")
                    st.rerun()

        else:
            st.warning("You haven't saved any places yet. Go to the 'Search Places' page to find and save destinations!")

    # Analysis Page
    elif selected_page == "📊 Analysis":
        df = load_dataset()
        if df.empty: return

        st.markdown("<h2 style='text-align: center;'>📊 Analysis of Tourist Places</h2>", unsafe_allow_html=True)
        st.write(f"- 🏔 Total Number of Tourist Places: {len(df)}")
        st.write(f"- 🌎 Total Number of Countries Represented: {df['Country'].nunique()}")
        st.write(f"- ⭐ Average Rating of Places: {df['Reviews'].mean():.2f}")
        
        st.markdown("---")
        st.write("### 🌍 Top 10 Countries by Number of Tourist Places")
        top_10_countries = df['Country'].value_counts().nlargest(10)
        fig_bar = px.bar(top_10_countries,
                         x=top_10_countries.index,
                         y=top_10_countries.values,
                         labels={'x': 'Country', 'y': 'Number of Places'},
                         color=top_10_countries.index,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.write("### 🏕 Distribution by Adventure Level")
        adventure_counts = df['Adventure Level'].value_counts()
        fig_pie = px.pie(adventure_counts,
                         values=adventure_counts.values,
                         names=adventure_counts.index,
                         title='Adventure Level Distribution',
                         color_discrete_sequence=px.colors.sequential.Sunset)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("---")
        st.write("### ⭐ Top 5 Most Popular Tourist Places (by Rating)")
        top_places = df.sort_values(by="Reviews", ascending=False).head(5)
        st.table(top_places[["Tourist Place", "Country", "City", "Reviews"]])

    # Chatbot Page
    elif selected_page == "🤖 Chatbot":
        st.markdown("<h2 style='text-align: center;'>🤖 Travel Chatbot</h2>", unsafe_allow_html=True)
        
        chatbot_responses = {
    "What are the best places to visit in Paris?": "Some of the best places to visit in Paris are the Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, and the Champs-Élysées.",
    "When is the best time to visit Bali?": "The best time to visit Bali is from April to October during the dry season.",
    "What are the top adventure destinations in India?": "Some top adventure destinations in India are Ladakh for biking, Rishikesh for river rafting, Andaman for scuba diving, and Spiti Valley for trekking.",
    "Can you suggest budget-friendly travel destinations?": "Some budget-friendly travel destinations are Vietnam, Thailand, Nepal, Indonesia, and Turkey.",
    "What is the best place for a honeymoon trip?": "The best honeymoon destinations include Maldives, Santorini, Paris, Bali, and Venice.",
    "Which country has the best beaches?": "Countries with the best beaches include the Maldives, Seychelles, Thailand, Australia, and Greece.",
    "Where can I see the Northern Lights?": "The Northern Lights can be seen in Norway, Iceland, Sweden, Finland, and Canada.",
    "What are the best places to visit in Dubai?": "The best places to visit in Dubai include Burj Khalifa, Dubai Mall, Palm Jumeirah, and Desert Safari.",
    "Where can I go for a peaceful and quiet vacation?": "Some peaceful destinations include Bhutan, Faroe Islands, New Zealand, and the Swiss Alps.",
    "Which are the best eco-friendly travel destinations?": "Best eco-travel spots include Costa Rica, Norway, Bhutan, and New Zealand.",
    "What are the top historical places in Rome?": "Top historical places in Rome include the Colosseum, Pantheon, Roman Forum, and St. Peter's Basilica.",
    "What are the most famous landmarks in London?": "Famous landmarks in London include Big Ben, Tower of London, Buckingham Palace, and London Eye.",
    "Which are the best ski resorts in Switzerland?": "Best ski resorts in Switzerland include Zermatt, St. Moritz, Verbier, and Engelberg.",
    "What are the must-visit places in Japan?": "Must-visit places in Japan include Mount Fuji, Kyoto, Tokyo Tower, and Hiroshima Peace Memorial.",
    "Which city is known as the Venice of the East?": "Udaipur in India is known as the Venice of the East due to its beautiful lakes and palaces.",
    "What are the best summer destinations in Europe?": "Best summer destinations in Europe include Santorini, Amalfi Coast, Barcelona, and the French Riviera.",
    "What are the safest countries for solo travelers?": "Some of the safest countries for solo travelers are Iceland, Japan, Switzerland, Canada, and New Zealand.",
    "Where can I experience the best wildlife safari?": "The best wildlife safaris are in Maasai Mara (Kenya), Kruger National Park (South Africa), and Serengeti (Tanzania).",
    "What are the best places for food lovers?": "Best places for food lovers include Bangkok, Tokyo, Paris, Istanbul, and Mexico City.",
    "Which cities have the best nightlife?": "Cities with the best nightlife include Las Vegas, Berlin, Amsterdam, Bangkok, and Ibiza.",
    "What are the best islands to visit in the Caribbean?": "Best Caribbean islands include Barbados, St. Lucia, Jamaica, and the Bahamas.",
    "Which are the top luxury travel destinations?": "Top luxury destinations include Dubai, Monaco, Maldives, Seychelles, and Bora Bora.",
    "What are the best places to visit in Australia?": "Best places in Australia include Sydney Opera House, Great Barrier Reef, Uluru, and Melbourne.",
    "What is the best time to visit Japan?": "The best time to visit Japan is during cherry blossom season (March-April) or autumn (September-November).",
    "What are the best places for a road trip in the USA?": "Best road trip routes in the USA include Route 66, Pacific Coast Highway, and Blue Ridge Parkway.",
    "Which countries are the most visa-friendly for travelers?": "Most visa-friendly countries include Indonesia, Thailand, Georgia, and Serbia.",
    "What are the best places to visit in South America?": "Top places in South America include Machu Picchu, Iguazu Falls, Patagonia, and the Amazon Rainforest.",
    "Which are the best cities to visit in Canada?": "Best cities in Canada include Vancouver, Toronto, Montreal, and Quebec City.",
    "Where can I go for an offbeat travel experience?": "Offbeat travel spots include Svalbard (Norway), Bhutan, Faroe Islands, and Socotra (Yemen).",
    "What are the best street food destinations in the world?": "Best street food destinations include Bangkok, Mexico City, Istanbul, Mumbai, and Ho Chi Minh City.",
    "What are the best places for cultural experiences?": "Best cultural destinations include Kyoto, Cairo, Varanasi, Marrakech, and Athens.",
    "Where are the most beautiful waterfalls in the world?": "Top waterfalls include Iguazu Falls, Victoria Falls, Angel Falls, and Niagara Falls.",
    "Which are the best train journeys in the world?": "Best train journeys include the Trans-Siberian Railway, Glacier Express, and the Orient Express.",
    "What are the best places to see cherry blossoms?": "Best places for cherry blossoms include Japan, Washington D.C., South Korea, and Paris.",
    "Which are the most romantic destinations?": "Most romantic destinations include Venice, Paris, Santorini, Prague, and Kyoto.",
    "What are the best places to visit in New Zealand?": "Best places in New Zealand include Milford Sound, Queenstown, Rotorua, and Wellington.",
    "Where are the best hiking destinations?": "Best hiking destinations include Patagonia, Himalayas, Rocky Mountains, and the Dolomites.",
    "Which countries have the best cultural festivals?": "Best cultural festivals include Carnival (Brazil), Oktoberfest (Germany), Holi (India), and La Tomatina (Spain).",
    "What are the best places to visit in Egypt?": "Best places in Egypt include the Pyramids of Giza, Luxor, Nile River, and the Red Sea.",
    "Where can I go for the best snorkeling experience?": "Best snorkeling spots include the Maldives, Great Barrier Reef, Red Sea, and Raja Ampat.",
    "What are the best places for winter travel?": "Best winter destinations include Lapland, Canada, Switzerland, and Japan’s ski resorts.",
    "What are the most unique places to visit?": "Most unique places include Salar de Uyuni, Cappadocia, Antelope Canyon, and the Great Blue Hole.",
    "Which cities have the best Christmas markets?": "Best Christmas markets include Vienna, Prague, Strasbourg, and Nuremberg.",
    "What are the most beautiful villages in the world?": "Most beautiful villages include Hallstatt (Austria), Shirakawa-go (Japan), and Reine (Norway).",
    "Where can I see the best autumn foliage?": "Best autumn foliage spots include Kyoto, Vermont (USA), Bavaria (Germany), and Quebec.",
    "What are the most underrated travel destinations?": "Underrated destinations include Albania, Georgia, Madagascar, and Bolivia.",
    "Where can I experience the best desert landscapes?": "Best deserts include the Sahara, Atacama, Wadi Rum, and the Namib Desert.",
    "What are the best UNESCO World Heritage sites?": "Top UNESCO sites include Machu Picchu, Petra, Great Wall of China, and Angkor Wat.",
} # Truncated for brevity
        suggested_questions = list(chatbot_responses.keys())
        selected_question = st.selectbox("Select a question:", ["Choose a question..."] + suggested_questions)
        query_to_ask = selected_question if selected_question != "Choose a question..." else ""

        if st.button("💬 Get Answer"):
            if not query_to_ask:
                st.warning("Please select a question.")
            elif query_to_ask in chatbot_responses:
                st.success(chatbot_responses[query_to_ask])
            else:
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful travel assistant."},
                            {"role": "user", "content": query_to_ask}
                        ]
                    )
                    st.success(response["choices"][0]["message"]["content"])
                except Exception as e:
                    st.error(f"Error fetching response from OpenAI. Ensure your API key is correct. Error: {e}")
    
    # Close the main app container
    st.markdown('</div>', unsafe_allow_html=True)

# ===== Authentication Interface =====
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""

if not st.session_state['logged_in']:
    # Add the animated gradient background for login/signup
    st.markdown('<div class="login-background"></div>', unsafe_allow_html=True)
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Stylish title with emojis and shadow effect
        st.markdown("""
            <h1 class="main-title">✈️ 🧳 🌍 Tourist HotSpot Finder</h1>
            <p class="subtitle">Your ultimate guide to the world's wonders</p>
        """, unsafe_allow_html=True)
        
        # Form container
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        choice = st.radio("", ["Login", "Sign Up"], horizontal=True)

        if choice == 'Login':
            st.subheader("Login")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type='password', key="login_pass")
            if st.button("Login"):
                if username and password:
                    user = users_collection.find_one({"username": username})
                    if user and check_hashes(password, user['password']):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.warning("Please enter both username and password.")

        elif choice == 'Sign Up':
            st.subheader("Create New Account")
            new_username = st.text_input("Username", key="signup_user")
            new_password = st.text_input("Password", type='password', key="signup_pass")
            if st.button("Sign Up"):
                if new_username and new_password:
                    if users_collection.find_one({"username": new_username}):
                        st.warning("Username already exists. Please choose another one.")
                    else:
                        hashed_password = make_hashes(new_password)
                        users_collection.insert_one({"username": new_username, "password": hashed_password})
                        st.success("You have successfully created an account! Please go to the Login page.")
                else:
                    st.warning("Please enter both a username and password.")
        
        st.markdown('</div>', unsafe_allow_html=True)
else:
    main_app()