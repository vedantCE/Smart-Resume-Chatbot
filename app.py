from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
import requests

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Function to get response from Gemini
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

# Function to process uploaded PDF
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to fetch YouTube video suggestions
def get_youtube_videos(query, max_results=3):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}&maxResults={max_results}&type=video"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("items", [])
        videos = []
        for item in results:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            videos.append({"title": title, "thumbnail": thumbnail, "url": video_url})
        return videos
    else:
        return []

# ------------------ Streamlit App ------------------

st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Job description input
input_text = st.text_area("Job Description: ", key="input")

# Resume upload
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ PDF Uploaded Successfully")

# Buttons
submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. 
Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. 
Give me the percentage of match if the resume matches the job description. 
First, the output should come as a percentage, then list keywords missing, and finally provide final thoughts.
"""

# Handle button clicks
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("The Response is:")
        st.write(response)

        # Show YouTube video suggestions
        st.subheader("🎥 Recommended YouTube Resources")
        videos = get_youtube_videos("how to improve resume for ATS")
        for v in videos:
            st.markdown(f"**{v['title']}**")
            st.image(v["thumbnail"], use_column_width=True)
            st.markdown(f"[▶ Watch on YouTube]({v['url']})")
            st.write("---")

    else:
        st.warning("⚠️ Please upload the resume first")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("The Response is:")
        st.write(response)

        # Show YouTube video suggestions
        st.subheader("🎥 Recommended YouTube Resources")
        videos = get_youtube_videos("ATS resume optimization tips")
        for v in videos:
            st.markdown(f"**{v['title']}**")
            st.image(v["thumbnail"], use_column_width=True)
            st.markdown(f"[▶ Watch on YouTube]({v['url']})")
            st.write("---")

    else:
        st.warning("⚠️ Please upload the resume first")
