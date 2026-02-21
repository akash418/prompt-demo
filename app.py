import streamlit as st
from openai import OpenAI
import time
import os
from jinja2 import Environment, FileSystemLoader, Template
import json
from pathlib import Path

# ============= PAGE CONFIGURATION =============
st.set_page_config(
    page_title="Real Estate Exposé Generator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============= CUSTOM CSS FOR BETTER UI =============
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .response-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #FF4B4B;
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
    }
    .stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: 600;
    }
    .property-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
    }
    .property-label {
        font-weight: 600;
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# ============= CONFIGURATION =============
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0.9
MAX_TOKENS = 800

# ============= LOAD JINJA2 TEMPLATE =============
@st.cache_resource
def load_template():
    """Load the Jinja2 template from file."""
    try:
        # Assuming template file is in the same directory as app.py
        template_path = Path("expose_template.j2")
        if template_path.exists():
            env = Environment(loader=FileSystemLoader("."))
            template = env.get_template("expose_template.j2")
            return template
        else:
            st.error("❌ Template file 'expose_template.j2' not found in current directory!")
            return None
    except Exception as e:
        st.error(f"❌ Error loading template: {str(e)}")
        return None

# ============= HEADER SECTION =============
st.markdown('<p class="main-header">🏠 Real Estate Exposé Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate professional property descriptions using AI</p>', unsafe_allow_html=True)

# ============= SIDEBAR FOR CONFIGURATION =============
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This tool generates professional real estate exposés in German using AI.

    **Model:** GPT-3.5-Turbo
    **Temperature:** 0.9
    **Max Tokens:** 800
    """)

    st.divider()

    st.header("📋 Instructions")
    st.markdown("""
    1. Fill in the property details
    2. Select target audience and style
    3. Click "Generate Exposé"
    4. Download the result
    """)

# ============= MAIN CONTENT AREA =============
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🏷️ Property Details")

    # Load template
    template = load_template()

    # Basic Information
    with st.expander("📋 Basic Information", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            estate_type = st.selectbox(
                "**Immobilientyp**",
                ["Haus", "Wohnung", "Grundstück", "Gewerbe"],
                index=0
            )
            estate_subtype = st.text_input("**Immobilien-Subtyp**", value="Einfamilienhaus")
            town = st.text_input("**Stadt**", value="Berlin")
            zip_code = st.text_input("**PLZ**", value="10115")

        with col_b:
            purchase_price = st.number_input("**Kaufpreis (€)**", min_value=0, value=500000, step=10000)
            living_space = st.number_input("**Wohnfläche (m²)**", min_value=0, value=120, step=10)
            realty_area = st.number_input("**Grundstücksfläche (m²)**", min_value=0, value=300, step=50)

    # Rooms and Features
    with st.expander("🛏️ Rooms & Layout", expanded=True):
        col_c, col_d, col_e = st.columns(3)
        with col_c:
            rooms = st.number_input("**Zimmer gesamt**", min_value=1, value=4, step=1)
        with col_d:
            bed_rooms = st.number_input("**Schlafzimmer**", min_value=0, value=3, step=1)
        with col_e:
            bath_rooms = st.number_input("**Badezimmer**", min_value=0, value=2, step=1)

    # Construction Details
    with st.expander("🏗️ Construction Details", expanded=True):
        col_f, col_g = st.columns(2)
        with col_f:
            construction_year = st.number_input("**Baujahr**", min_value=1800, max_value=2025, value=2005, step=1)
            condition = st.selectbox(
                "**Zustand**",
                ["Erstbezug", "Neuwertig", "Gepflegt", "Modernisiert", "Renovierungsbedürftig"],
                index=2
            )
        with col_g:
            energy_rating = st.selectbox(
                "**Energieeffizienzklasse**",
                ["A+", "A", "B", "C", "D", "E", "F", "G", "H"],
                index=3
            )
            energy_consumption = st.number_input("**Energieverbrauch (kWh/(m²a))**", min_value=0, value=120, step=5)

    # Equipment and Features
    with st.expander("🔧 Ausstattung", expanded=True):
        col_h, col_i = st.columns(2)
        with col_h:
            heating = st.selectbox(
                "**Heizung**",
                ["Gasheizung", "Ölheizung", "Fernwärme", "Wärmepumpe", "Fußbodenheizung", "Nachtspeicher"],
                index=0
            )
            firing = st.selectbox(
                "**Energiequelle**",
                ["Gas", "Öl", "Erdwärme", "Luftwärme", "Pellets", "Fernwärme"],
                index=0
            )
        with col_i:
            floorings = st.multiselect(
                "**Bodenbeläge**",
                ["Parkett", "Laminat", "Fliesen", "Teppich", "Naturstein", "Dielen"],
                default=["Parkett", "Fliesen"]
            )
            furnishing = st.text_input("**Ausstattung**", value="Moderne Einbauküche, Badezimmer mit Fenster")

    # Outdoor Features
    with st.expander("🌳 Außenbereich", expanded=True):
        col_j, col_k = st.columns(2)
        with col_j:
            garden = st.selectbox("**Garten**", ["Ja", "Nein", "Teilweise"], index=0)
        with col_k:
            garage = st.selectbox("**Garagen**", ["Ja", "Nein"], index=0)
            if garage == "Ja":
                garages = st.number_input("**Anzahl Garagen**", min_value=1, value=1, step=1)
            else:
                garages = 0

            parking_spaces = st.number_input("**Parkplätze**", min_value=0, value=1, step=1)

    # Special Features
    with st.expander("✨ Besondere Merkmale", expanded=False):
        features = st.text_area(
            "**Besondere Merkmale (ein pro Zeile)**",
            value="Denkmalgeschützt\nAufzug\nKamin\nGäste-WC",
            help="Jedes Merkmal in eine neue Zeile"
        )
        feature_list = [f.strip() for f in features.split("\n") if f.strip()]

    # Target Group and Style
    st.header("🎯 Generation Settings")
    col_l, col_m = st.columns(2)
    with col_l:
        target_group = st.selectbox(
            "**Zielgruppe**",
            ["Familien", "Geschäftsleute", "Investoren", "Senioren", "Paare"],
            index=0
        )
    with col_m:
        text_style = st.selectbox(
            "**Textstil**",
            ["Ausführlich", "Kompakt", "Standard"],
            index=2
        )

    # Generate button
    generate_button = st.button("🚀 Generate Exposé", use_container_width=True)

with col2:
    st.header("📄 Generated Exposé")

    # Function to prepare property data
    def prepare_property_data():
        """Prepare property data in the format expected by the template."""
        property_data = {
            "expose_object": {
                "object_attributes": {
                    "estateType": estate_type,
                    "estateSubType": estate_subtype,
                    "town": town,
                    "zip": zip_code,
                    "purchasePrice": purchase_price,
                    "livingSpace": living_space,
                    "realtyArea": realty_area,
                    "rooms": rooms,
                    "bedRooms": bed_rooms,
                    "bathRooms": bath_rooms,
                    "constructionYearNumber": construction_year,
                    "condition": condition,
                    "energyEfficiencyRating": energy_rating,
                    "energyConsumption": energy_consumption,
                    "heatings": heating,
                    "firings": firing,
                    "floorings": floorings,
                    "furnishing": furnishing,
                    "garden": garden,
                    "garages": garages if garage == "Ja" else 0,
                    "parkingSpaces": parking_spaces,
                    "estateDefaultFeatures": feature_list
                }
            },
            "target_group": target_group,
            "text_style": text_style
        }
        return property_data

    # Handle generate button click
    if generate_button:
        if template is None:
            st.error("⚠️ Template file not found. Please ensure 'expose_template.j2' exists.")
        elif not hasattr(st, 'secrets') or not st.secrets.get("OPENAI_API_KEY"):
            st.error("⚠️ OpenAI API key not found in secrets. Please add it to your Streamlit secrets.")
        else:
            try:
                # Prepare property data
                property_data = prepare_property_data()

                # Render the template
                rendered_prompt = template.render(**property_data)

                # Display the prompt being sent (optional)
                with st.expander("📤 View prompt sent to model"):
                    st.text(rendered_prompt)

                # Show loading spinner
                with st.spinner("Generating exposé..."):
                    # Initialize OpenAI client
                    api_key = st.secrets["OPENAI_API_KEY"]
                    client = OpenAI(api_key=api_key)

                    # Make API call
                    start_time = time.time()
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "You are a professional real estate exposé writer. Generate accurate, well-structured property descriptions in German."},
                            {"role": "user", "content": rendered_prompt}
                        ],
                        temperature=TEMPERATURE,
                        max_tokens=MAX_TOKENS,
                        top_p=0.95,
                    )
                    end_time = time.time()

                    # Extract response text
                    model_response = response.choices[0].message.content

                    # Display response in a nice box
                    st.markdown('<div class="response-box">', unsafe_allow_html=True)
                    st.markdown(model_response)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Show metadata
                    st.caption(f"⏱️ Generation time: {end_time - start_time:.2f}s")

                    # Export options
                    st.download_button(
                        label="📥 Download Exposé as Text",
                        data=model_response,
                        file_name=f"expose_{town}_{target_group}_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ============= FOOTER =============
st.divider()
col_left, col_right = st.columns([3, 1])
with col_left:
    st.caption("Built with Streamlit • Powered by OpenAI • Jinja2 Template")
with col_right:
    st.caption(f"v1.0.0")