import streamlit as st
from openai import OpenAI
import time
import os

# ============= PAGE CONFIGURATION =============
st.set_page_config(
    page_title="LLM Playground",
    page_icon="🤖",
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
    }
    .stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============= SESSION STATE INITIALIZATION =============
if 'response_history' not in st.session_state:
    st.session_state.response_history = []

# ============= HEADER SECTION =============
st.markdown('<p class="main-header">🤖 LLM Playground</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Interact with language models through a simple interface</p>', unsafe_allow_html=True)

# ============= SIDEBAR FOR CONFIGURATION =============
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Key input (with option to use secrets)
    api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key. It will not be stored or shared.",
        value=st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, 'secrets') else ""

    )

    # Model selection
    model_options = ["gpt-3.5-turbo"]
    selected_model = st.selectbox(
        "Select Model",
        model_options,
        index=0,
        help="Choose which OpenAI model to use"
    )

    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more random, lower values more deterministic"
    )

    # Max tokens
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=50,
        max_value=4000,
        value=500,
        step=50,
        help="Maximum length of the response"
    )

    st.divider()

    # Clear history button
    if st.button("🗑️ Clear Response History"):
        st.session_state.response_history = []
        st.rerun()

# ============= MAIN CONTENT AREA =============
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Input Fields")

    # Text input for topic
    topic = st.text_input(
        "**Topic**",
        value="The future of artificial intelligence",
        placeholder="Enter a topic...",
        help="The main subject you want the model to write about"
    )

    # Selectbox for style
    style = st.selectbox(
        "**Writing Style**",
        ["Formal", "Casual", "Funny", "Poetic", "Technical", "Inspirational"],
        index=0,
        help="Choose the tone of the response"
    )

    # Multiselect for additional elements
    elements = st.multiselect(
        "**Include Elements**",
        ["Examples", "Statistics", "Quotes", "Jokes", "Historical context"],
        default=["Examples"],
        help="Optional elements to include in the response"
    )

    # Text area for additional instructions
    instructions = st.text_area(
        "**Additional Instructions** (optional)",
        placeholder="E.g., 'Keep it under 100 words' or 'Focus on benefits'",
        height=100
    )

    # Number of paragraphs
    num_paragraphs = st.number_input(
        "**Number of Paragraphs**",
        min_value=1,
        max_value=5,
        value=1,
        step=1
    )

    # Generate button
    generate_button = st.button("🚀 Generate Response", use_container_width=True)

with col2:
    st.header("🤖 Model Response")

    # Function to construct prompt from inputs
    def construct_prompt(topic, style, elements, instructions, num_paragraphs):
        elements_text = ", ".join(elements) if elements else "no specific elements"

        prompt = f"""Write a {style.lower()} response about "{topic}".

Requirements:
- Write {num_paragraphs} paragraph(s)
- Include the following elements if relevant: {elements_text}
"""
        if instructions:
            prompt += f"\nAdditional instructions: {instructions}"

        prompt += "\n\nResponse:"
        return prompt

    # Handle generate button click
    if generate_button:
        if not api_key_input and not (hasattr(st, 'secrets') and st.secrets.get("OPENAI_API_KEY")):
            st.error("⚠️ Please enter your OpenAI API key in the sidebar or add it to secrets.")
        else:
            # Construct the prompt
            full_prompt = construct_prompt(topic, style, elements, instructions, num_paragraphs)

            # Display the prompt being sent (optional)
            with st.expander("📤 View prompt sent to model"):
                st.text(full_prompt)

            # Show loading spinner
            with st.spinner("Model is thinking..."):
                try:
                    # Initialize OpenAI client
                    api_key = api_key_input or st.secrets["OPENAI_API_KEY"]
                    client = OpenAI(api_key=api_key)

                    # Make API call
                    start_time = time.time()
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": "You are a helpful, creative, and accurate assistant."},
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=0.95,
                    )
                    end_time = time.time()

                    # Extract response text
                    model_response = response.choices[0].message.content

                    # Store in session state
                    st.session_state.response_history.append({
                        "topic": topic,
                        "style": style,
                        "response": model_response,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })

                    # Display response in a nice box
                    st.markdown('<div class="response-box">', unsafe_allow_html=True)
                    st.markdown(model_response)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Show metadata
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.caption(f"⏱️ Response time: {end_time - start_time:.2f}s")
                    with col_b:
                        st.caption(f"🎯 Model: {selected_model}")
                    with col_c:
                        st.caption(f"🌡️ Temperature: {temperature}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Make sure your API key is correct and you have sufficient credits.")

# ============= RESPONSE HISTORY SECTION =============
if st.session_state.response_history:
    st.divider()
    st.header("📜 Response History")

    # Create columns for history items
    history_cols = st.columns(3)

    for idx, item in enumerate(reversed(st.session_state.response_history[-6:])):
        col_idx = idx % 3
        with history_cols[col_idx]:
            with st.container(border=True):
                st.caption(f"🕐 {item['timestamp']}")
                st.markdown(f"**{item['topic'][:50]}...**" if len(item['topic']) > 50 else f"**{item['topic']}**")
                st.markdown(f"*Style: {item['style']}*")
                if st.button(f"View #{len(st.session_state.response_history) - idx}", key=f"view_{idx}"):
                    st.session_state.viewing_history = item['response']

    # Show full history response if selected
    if 'viewing_history' in st.session_state:
        with st.expander("📄 Selected Response", expanded=True):
            st.markdown(st.session_state.viewing_history)

# ============= FOOTER =============
st.divider()
col_left, col_right = st.columns([3, 1])
with col_left:
    st.caption("Built with Streamlit • Powered by OpenAI")
with col_right:
    st.caption(f"v1.0.0")

# ============= RUN INSTRUCTIONS =============
# To run this app:
# 1. Save this file as app.py
# 2. Install requirements: pip install streamlit openai
# 3. Run: streamlit run app.py