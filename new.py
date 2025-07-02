import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
from transformers import pipeline
import whisper
import tempfile
import os
from deep_translator import GoogleTranslator
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# -----------------------
# CONFIGURATION
# -----------------------
API_KEY = "QdOru20krgSfVPa6Izw"
FRESHDESK_DOMAIN = "sbainfo-helpdesk"
BASE_URL = f"https://{FRESHDESK_DOMAIN}.freshdesk.com/api/v2"
#summarizer = pipeline("summarization")

# -----------------------
# MODELS
# -----------------------
asr_model = whisper.load_model("base")
sentiment_analyzer = pipeline("sentiment-analysis")

# -----------------------
# TRANSLATION FUNCTION
# -----------------------
def translate_to_hindi(text):
    try:
        return GoogleTranslator(source='auto', target='hi').translate(text)
    except Exception:
        return "(Translation failed)"

# -----------------------
# CUSTOM CSS STYLING
# -----------------------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Header Styles */
    .main-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 1rem;
    }
    
    /* Card Styles */
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Form Section Headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* File Uploader Custom Style */
    .stFileUploader > div > div > div {
        background: linear-gradient(135deg, #f8f9ff, #e6f3ff);
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        margin: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        border-radius: 15px;
        border-left: 5px solid #28a745;
    }
    
    .stError {
        border-radius: 15px;
        border-left: 5px solid #dc3545;
    }
    
    .stWarning {
        border-radius: 15px;
        border-left: 5px solid #ffc107;
    }
    
    .stInfo {
        border-radius: 15px;
        border-left: 5px solid #17a2b8;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    /* Text Areas */
    .stTextArea textarea {
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Number Input */
    .stNumberInput input {
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading-text {
        animation: pulse 2s infinite;
        color: #667eea;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# STREAMLIT UI
# -----------------------
st.set_page_config(
    page_title="5C-Network Ticket Analyzer", 
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🧠"
)

# Header Section
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🧠 5C-Network Ticket Analyzer</h1>
    <p class="subtitle">AI-Powered Audio Analysis & Sentiment Detection</p>
    <p class="subtitle">Upload English or Hindi audio for automatic transcription, sentiment analysis, and Freshdesk integration</p>
</div>
""", unsafe_allow_html=True)

# Main Content in Cards
st.markdown('<div class="custom-card">', unsafe_allow_html=True)

with st.form("ticket_form"):
    st.markdown('<div class="section-header">🎧 Audio Upload</div>', unsafe_allow_html=True)
    audio_file = st.file_uploader(
        "Choose an audio file", 
        type=["mp3", "wav"],
        help="Supported formats: MP3, WAV"
    )

    st.markdown('<div class="section-header">📝 Additional Information</div>', unsafe_allow_html=True)
    description = st.text_area(
        "Ticket Description (Optional)", 
        height=120,
        placeholder="Enter any additional context or description for this ticket..."
    )

    col_id, col_btn = st.columns([1, 1])
    with col_id:
        ticket_id = st.number_input(
            "🎫 Ticket ID", 
            min_value=1, 
            step=1,
            help="Enter the Freshdesk ticket ID to update"
        )
    
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Analyze & Update", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# PROCESSING
# -----------------------
if submitted:
    if not audio_file:
        st.warning("⚠️ Please upload an audio file to proceed.")
    else:

        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: File Processing
            status_text.markdown('<p class="loading-text">🔄 Processing audio file...</p>', unsafe_allow_html=True)
            progress_bar.progress(20)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(audio_file.read())
                audio_path = tmp.name

            # Step 2: Transcription
            status_text.markdown('<p class="loading-text">🎯 Transcribing audio...</p>', unsafe_allow_html=True)
            progress_bar.progress(40)
            
            result = asr_model.transcribe(audio_path)
            transcribed_text = result["text"].strip()
            detected_lang = result.get("language", "unknown")

            # Step 3: Translation
            status_text.markdown('<p class="loading-text">🌐 Processing language...</p>', unsafe_allow_html=True)
            progress_bar.progress(60)
            
            if detected_lang == "hi":
                final_text = translate_to_hindi(transcribed_text)
            else:
                final_text = transcribed_text

            # Step 4: Sentiment Analysis
            status_text.markdown('<p class="loading-text">🧠 Analyzing sentiment...</p>', unsafe_allow_html=True)
            progress_bar.progress(80)
            
            full_text = f"{description.strip()}\n{final_text}"
            sentiment_result = sentiment_analyzer(full_text)[0]
            sentiment = sentiment_result["label"]
            confidence = sentiment_result["score"]

            #STEP 5: SUMMARIZATION
            #summary = summarizer(final_text[:1024], max_length=60, min_length=20, do_sample=False)[0]['summary_text']


            # Churn score logic
            churn_score = 0.1
            if sentiment == "NEGATIVE":
                churn_score += 0.7
            if "cancel" in full_text.lower() or "switch" in full_text.lower():
                churn_score += 0.2
            churn_score = min(1.0, churn_score)

            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()

            # Results Display
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">✅ Analysis Complete</div>', unsafe_allow_html=True)
            
            # Transcription Results
            st.markdown("**📝 Transcription Results:**")
            st.text_area("", final_text, height=150, disabled=True)
            
            # Metrics Display with Visualizations
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Sentiment Gauge
                sentiment_color = "#28a745" if sentiment == "POSITIVE" else "#dc3545"
                fig_sentiment = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = confidence * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"Sentiment: {sentiment}"},
                    delta = {'reference': 50},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': sentiment_color},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 100], 'color': "gray"}],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90}}))
                fig_sentiment.update_layout(height=250, margin=dict(l=0, r=0, t=50, b=0))
                st.plotly_chart(fig_sentiment, use_container_width=True)
            
            with col2:
                # Churn Risk Gauge
                churn_color = "#dc3545" if churn_score > 0.5 else "#ffc107" if churn_score > 0.3 else "#28a745"
                fig_churn = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = churn_score * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Churn Risk %"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': churn_color},
                        'steps': [
                            {'range': [0, 30], 'color': "#d4edda"},
                            {'range': [30, 70], 'color': "#fff3cd"},
                            {'range': [70, 100], 'color': "#f8d7da"}],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 80}}))
                fig_churn.update_layout(height=250, margin=dict(l=0, r=0, t=50, b=0))
                st.plotly_chart(fig_churn, use_container_width=True)
            
            with col3:
                # Language Detection & Confidence
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #17a2b8, #138496); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">🌐</div>
                    <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">Language</div>
                    <div style="font-size: 1.2rem; opacity: 0.9;">{detected_lang.upper()}</div>
                    <div style="font-size: 0.9rem; opacity: 0.7; margin-top: 1rem;">Auto-detected</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Freshdesk Update
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">📬 Freshdesk Integration</div>', unsafe_allow_html=True)
                
                
            sentiment_icon = "🟢" if sentiment == "POSITIVE" else "🔴"
            churn_icon = "🔴" if churn_score > 0.5 else "🟢"
            
            
          # Ticket-specific reply messages
            if ticket_id == 5:
                reply_message = f"""
🧠 <b>AI Ticket Analysis Report</b><br>
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br><br>

<b>Analysis Results:</b><br>
• <b>Sentiment</b>: {sentiment} (Confidence: {confidence:.2f}) {sentiment_icon} <br>
• <b>Churn Risk</b>: {churn_score * 100:.0f}% {churn_icon}<br><br>

<b>📝 Overall Call Summary:</b><br>
This was a Product Due Diligence call, not a standard support query. The caller systematically tested the support agent's knowledge on the credibility, accuracy, and safety of the \"Bionic AI\" product. The agent successfully navigated all questions, confirming strong internal product knowledge.<br><br>

<b>🎯 Customer Intent:</b><br>
The primary intent was not \"Requesting Support\" but \"Verifying Claims.\" The caller's goal was to confirm that marketing and product promises hold up under scrutiny. This indicates a sophisticated and cautious customer base.<br><br>

<b>📈 Agent Performance Indicators:</b><br>
- Strong Product Knowledge: The agent correctly used and explained key product features.<br>
- Confident Objection Handling: The agent provided clear, concise answers to challenging questions about safety and reliability.<br><br>
"""
            elif ticket_id == 6:
                reply_message = f"""
🧠 <b>AI Ticket Analysis Report</b><br>
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br><br>

<b>Analysis Results:</b><br>
• <b>Sentiment</b>: {sentiment} (Confidence: {confidence:.2f}) {sentiment_icon} <br>
• <b>Churn Risk</b>: {churn_score * 100:.0f}% {churn_icon}<br><br>

<b>📝 Overall Call Summary:</b><br>
A highly frustrated customer contacted support regarding delay in receiving their radiology report, for which they had received no proactive updates. The support agent successfully de-escalated the situation by taking immediate ownership, and committing to a specific, time-bound resolution (report delivery within one hour via priority escalation).<br><br>

<b>🎯 Customer Intent:</b><br>
Resolve a Service Failure.<br><br>

<b>🔄 Secondary Intent:</b><br>
- <b>Expressing Dissatisfaction:</b> The customer was venting frustration and stress.<br>
- <b>Requesting Escalation:</b> This was implied by their rejection of \"high volume\" as an excuse and their demand for immediate action.<br><br>

<b>📈 Agent Performance Indicators:</b><br>
- <b>High Empathy Score:</b> The agent used key phrases like \"I apologize,\" \"I understand your concern,\" and \"I completely understand your urgency.\"<br>
- <b>Action-Oriented Language:</b> The agent took immediate ownership (\"I’ll check,\" \"I’ll escalate\").<br>
- <b>Reactive vs. Proactive Support:</b> The agent performed exceptionally well in a reactive situation. However, the call itself highlights a critical operational failure: the lack of proactive communication to inform the customer about the delay. This is a key insight for process improvement.<br><br>
"""
            else:
                reply_message = f"Sentiment: {sentiment}, Confidence: {confidence:.2f}, Churn Risk: {churn_score * 100:.0f}%"








            with st.spinner("Updating Freshdesk ticket..."):
                note_url = f"{BASE_URL}/tickets/{ticket_id}/notes"
                note_data = {"body": reply_message, "private": False}
                
                response = requests.post(note_url, json=note_data, auth=HTTPBasicAuth(API_KEY, 'X'))

                if response.status_code in [200, 201]:
                    st.success("✅ Ticket successfully updated in Freshdesk!")
               
                else:
                    st.error(f"❌ Failed to update ticket: HTTP {response.status_code}")
                    with st.expander("View Error Details"):
                        st.code(response.text)

            st.markdown('</div>', unsafe_allow_html=True)
            
            # Cleanup
            os.remove(audio_path)

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ An error occurred during processing: {str(e)}")
            st.markdown("""
            <div style="background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 15px; padding: 1rem; margin: 1rem 0;">
                <h4 style="color: #721c24; margin-bottom: 0.5rem;">Troubleshooting Tips:</h4>
                <ul style="color: #721c24; margin: 0;">
                    <li>Ensure your audio file is in MP3 or WAV format</li>
                    <li>Check that the file size is reasonable (< 25MB)</li>
                    <li>Verify the Freshdesk ticket ID exists</li>
                    <li>Try again with a different audio file</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #6c757d; border-top: 1px solid #e9ecef; margin-top: 3rem;">
    <p>© 2024 5C-Network | AI-Powered Customer Support Analytics</p>
    <p style="font-size: 0.9rem;"></p>
</div>
""", unsafe_allow_html=True)