import streamlit as st
import pytube as pt
import os
import subprocess
import re
from utils import logtime, load_ffmpeg
import whisper
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

URL = 'URL'
TEXT = 'TEXT'
WHISPER = 'WHISPER'
PROCESSING = 'PROCESSING'
STATES = [URL, TEXT, WHISPER, PROCESSING]
AUDIO_FILE = "audio.mp3"
AUDIO_EXISTS = "AUDIO_EXISTS"
model = ''

st.title('Youtube Audio+Text')

def init_state():
    if URL not in st.session_state:
        st.session_state[URL] = ''
    
    if TEXT not in st.session_state:
        st.session_state[TEXT] = ''

    if WHISPER not in st.session_state:
        st.session_state[WHISPER] = ''

    if AUDIO_EXISTS not in st.session_state:
        st.session_state[AUDIO_EXISTS] = False
    
    if not st.session_state[URL]:
        clear_old_files()
        print("Clear old files")

def clear_old_files():
    for file in os.listdir():
        if file.endswith(".mp3") or file == 'transcript.txt':
            os.remove(file)
            print(f"Removed old files::{file}")

    
def extract_youtube_video_id(url):
  regex = r"v=([^&]+)"
  match = re.search(regex, url)
  if match:
    return match.group(1)
  else:
    return None

@logtime
def load_whisper():
    # if not model:
    model = whisper.load_model("small")
    print('Loaded Whisper Medium model')
    # else:
    #     print('Already downloaded Whisper model')
    print('Transcribing with Whisper model')
    result = model.transcribe("audio.mp3")
    st.session_state[WHISPER] = result["text"]
    write_file(result["text"], "whisper.txt")
AUDIO_FILE = "audio.mp3"

def load_audio():
    if os.path.exists(AUDIO_FILE):
        st.session_state[AUDIO_EXISTS] = True
        audio_file = open(AUDIO_FILE, 'rb')
        audio_bytes = audio_file.read()
        print(f"Audio file exists...{len(audio_bytes)}")
        st.audio(audio_bytes, format="audio/mp3")
    elif st.session_state[AUDIO_EXISTS]:
        st.session_state[AUDIO_EXISTS] = False

def display():
    container = st.container()
    text_container = st.container()
    # whisper_container = st.container()
    load_audio()

    #Download Button section
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state[AUDIO_EXISTS]:
            st.download_button("Download Audio","file","audio.mp3","application/octet-stream")
    with col2:
        if os.path.exists("transcript.txt"):
            st.download_button("Download Transcript",st.session_state[TEXT],"transcript.txt","text/plain")

    with container:
        with st.form(key='input_form'):
            user_input = st.text_input("Youtube URL:", placeholder="http://www.youtube.com", key=URL)
            input_submit_button = st.form_submit_button(label='Send')

    if input_submit_button and user_input:

        st.write("You entered... " + st.session_state[URL])
        # transcribe()
        # download()
        # download_audio()
        load_whisper()

    
    with text_container:
       st.text_area(label="Youtube Transcript:",
                    height=200,
                    value=st.session_state[TEXT])
    # with whisper_container:
    #    st.text_area(label="Whisper Transcript:",
    #                 height=200,
    #                 value=st.session_state[WHISPER])

@logtime
def download_audio():
    if st.session_state[URL]:
        print("Downloading....")
        yt = pt.YouTube(st.session_state[URL])
        stream = yt.streams.filter(only_audio=True)[0]
        stream.download(filename="audio.mp3")
        print("Downloaded Audio file....")

def download():
  id = extract_youtube_video_id(st.session_state[URL])
  command = [f"yt-dlp --no-config -v --extract-audio --audio-format mp3 {st.session_state[URL]} -o audio.mp3"]
  print(command)
  out = subprocess.run(command, shell=True)
  print('Download with YT-DLP done!!')

@logtime
def transcribe():
    loader = YoutubeLoader.from_youtube_url(
        st.session_state[URL], add_video_info=True)
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=500)
    docs = loader.load_and_split(splitter)
    length = len(docs)
    index = int(length/3+1)
    print(f"Loaded {length} documents, Displaying {index}-th document")
    # st.session_state[TEXT] = docs[index].page_content
    st.session_state[TEXT] = write_chunks(docs,"transcript.txt")

@logtime
def write_chunks(docs, filename):
    full_doc = ''
    for doc in docs:
       full_doc = full_doc + doc.page_content + "\n"
    with open(filename, "w") as f:
        f.write(full_doc)
        return full_doc

def write_file(text, filename):
    with open(filename, "w") as f:
        f.write(text)
        # return full_doc

def main():
    # load_ffmpeg()
    init_state()
    display()


if __name__ == "__main__":
    main()