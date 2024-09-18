import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from agents.chapter_notes import extract_chapters_notes, fmt_chapter_notes
from agents.chapter import extract_chapters, fmt_chapter
from agents.summary import extract_summary, fmt_summary
from dotenv import load_dotenv

load_dotenv()


def get_youtube_transcript(video_id: str) -> str:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return [f"ts={entry['start']} - {entry['text']}" for entry in transcript]
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return ""

st.set_page_config(layout="wide", page_title="Transcript Analysis", page_icon="📝")
st.title("📝 Transcript Analysis")


def process(transcript, generate_option):
    if generate_option == "summary":
        extract = extract_summary
        fmt = fmt_summary
    elif generate_option == "chapters":
        extract = extract_chapters
        fmt = fmt_chapter
    else:
        extract = extract_chapters_notes
        fmt = fmt_chapter_notes

    responses = extract(transcript)
    for response in responses:
        yield fmt(response)

    return

transcript = ""
col1, col2 = st.columns(2)
with col1:
    from_option = st.selectbox(
        "From",
        ["YouTube", "File"],
        index=0
    )
with col2:
    generate_option = st.selectbox(
        "Generate",
        ["summary", "chapters", "notes"],
        index=0
    )

if from_option == "YouTube":
    url_input = st.text_input(
        "Enter a URL:",
        value="https://www.youtube.com/watch?v=7aGTKJJMb5w",
    )
else:
    uploaded_file = st.file_uploader("Choose a text file")
    if uploaded_file is not None:
        transcript = uploaded_file.read().decode('utf-8')

if st.button("Submit"):
    if from_option == "YouTube":
        video_id = url_input.split("?v=")[-1].split("&")[0]
        transcript = get_youtube_transcript(video_id)
        transcript = ''.join(transcript)
    
    if transcript.rstrip() == "":
        raise ValueError("No transcript provided...")
    st.write("---")
    for content in process(transcript, generate_option):
        st.markdown(content)
