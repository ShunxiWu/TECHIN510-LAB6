import streamlit as st
import os
from dotenv import load_dotenv
import requests
import fitz
from openai import OpenAI

st.title("PDF to Text with ChatGPT")

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Upload PDF")

def extract_text_from_pdf(pdf_contents):
    doc = fitz.open(stream=pdf_contents, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    st.write("Extracted text from PDF:")
    st.write(text)  # 打印提取的文本内容
    return text

def send_openai_request(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    data = {
        "model": st.session_state["openai_model"],
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.7,
    }
    response = requests.post(f"{OPENAI_API_BASE}/completions", json=data, headers=headers, stream=True)
    return response.iter_lines()


if uploaded_file:
    pdf_contents = uploaded_file.read()
    text = extract_text_from_pdf(pdf_contents)

    # 构建用于 ChatGPT 的 prompt
    prompt = f"Read the following content, define what kind of document it is and generate text to latex by its content style, your output should only have 1. what kind of document it is 2. Generated to Latex:\n{text}\n\n"

    # 向会话消息列表中添加用户输入的 prompt
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})

