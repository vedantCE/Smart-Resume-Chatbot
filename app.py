import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import requests
from streamlit_chat import message  # Chatbot message bubble component

# Load environment variables
load_dotenv()

# Configure the Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# YouTube API Key from environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Function to get Gemini response
def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

# Function to extract text from uploaded PDF file
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# YouTube Video Search Function
def get_youtube_videos(query):
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}&maxResults=5"
    response = requests.get(search_url)
    videos = response.json().get('items', [])
    video_results = []

    for video in videos:
        video_title = video['snippet']['title']
        video_id = video['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_results.append((video_title, video_url))
    
    return video_results

# Streamlit Chatbot Interface
st.title("Smart ATS Chatbot")

# Set a technical robot background image
st.markdown(
    """
    <style>
    .background {
        background-image: url('https://example.com/path/to/your/robot-background.jpg');
        background-size: cover;
        background-position: center;
        height: 100vh;
        padding: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state to store messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Input widget for chat-like interface using text_area for larger input
user_input = st.text_area("Type your message here...", key="user_input", height=150)

# Function to handle the chat input
def handle_user_input(user_input):
    if user_input.lower() == "stop":
        st.session_state.messages.append({"role": "bot", "text": "Chatbot: Goodbye! If you need me again, just type your message."})
        st.stop()  # Stop the chat session
    elif user_input:
        st.session_state.messages.append({"role": "user", "text": user_input})
        return user_input
    return None

# Handle file upload
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf", key="file")

# Function to simulate bot response
def generate_response(jd, resume_text=None):
    if resume_text:
        input_prompt = f"""
        Act as an experienced ATS (Application Tracking System).
        You are given a resume and a job description.
        
        Your task is to:
        1. Calculate the percentage match between the resume and the job description.
        2. Identify any missing keywords from the resume that are present in the job description.
        3. Provide a profile summary.

        Resume: {resume_text}
        Job Description: {jd}

        Respond in this structure:
        {{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
        """
        bot_response = get_gemini_response(input_prompt)
    else:
        input_prompt = f"Answer this query: {jd}"
        bot_response = get_gemini_response(input_prompt)
    
    video_suggestions = get_youtube_videos(jd)
    video_links = "\n".join([f"- [{video_title}]({video_url})" for video_title, video_url in video_suggestions])

    # Combine bot response with video suggestions
    final_response = f"{bot_response}\n\nYouTube Video Suggestions:\n{video_links}"
    st.session_state.messages.append({"role": "bot", "text": final_response})

# Handle user input
if user_input:
    jd_input = handle_user_input(user_input)
    if uploaded_file is not None:
        resume_text = input_pdf_text(uploaded_file)
        generate_response(jd_input, resume_text)
    else:
        generate_response(jd_input)

# Automatically scroll to the latest message
if st.session_state.messages:
    for i, message_data in enumerate(st.session_state["messages"]):
        role = message_data["role"]
        text = message_data["text"]
        
        if role == "user":
            message(text, is_user=True, key=f"user_{i}")  # Unique key for user messages
        else:
            message(text, key=f"bot_{i}")  # Unique key for bot messages

# Add a button to send the message
if st.button("Send", key="send-button"):
    if user_input:
        st.session_state["user_input"] = user_input  # This line sets the user input correctly
        st.session_state["messages"].append({"role": "user", "text": user_input})
        # Reset the input field
        st.session_state["user_input"] = ""
