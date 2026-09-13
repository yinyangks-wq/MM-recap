import streamlit as st
from groq import Groq
from docx import Document
import pypdf

# Page Config
st.set_page_config(page_title="Unlimited Fast Translator", layout="wide")
st.title("🌐 Unlimited Fast Translator (Powered by Groq)")

# 50+ Popular Languages List
LANGUAGES = [
    "Afrikaans", "Albanian", "Arabic", "Armenian", "Bengali", "Bosnian", "Bulgarian", 
    "Burmese (Myanmar)", "Catalan", "Chinese (Simplified)", "Chinese (Traditional)", 
    "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Filipino", 
    "Finnish", "French", "German", "Greek", "Gujarati", "Hebrew", "Hindi", 
    "Hungarian", "Indonesian", "Italian", "Japanese", "Javanese", "Kannada", 
    "Khmer", "Korean", "Lao", "Malay", "Malayalam", "Marathi", "Nepali", 
    "Norwegian", "Persian", "Polish", "Portuguese", "Punjabi", "Romanian", 
    "Russian", "Serbian", "Sinhala", "Slovak", "Spanish", "Swahili", "Swedish", 
    "Tamil", "Telugu", "Thai", "Turkish", "Ukrainian", "Urdu", "Vietnamese"
]

# Sidebar - Settings
st.sidebar.header("⚙️ Settings")
api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

# Select Languages
col1, col2 = st.columns(2)
with col1:
    src_lang = st.selectbox("From (မူရင်းဘာသာစကား):", ["Auto Detect"] + LANGUAGES)
with col2:
    target_lang = st.selectbox("To (ပြန်ဆိုချင်သည့်ဘာသာစကား):", LANGUAGES, index=LANGUAGES.index("Burmese (Myanmar)"))

# Input Option (Text or File Upload)
input_type = st.radio("ဘာသာပြန်မည့် နည်းလမ်း ရွေးပါ -", ["Direct Text", "File Upload (.txt, .docx, .pdf)"])

input_text = ""

if input_type == "Direct Text":
    input_text = st.text_area("ဘာသာပြန်ချင်သည့် စာသားများကို အောက်တွင် ထည့်ပါ -", height=250)
else:
    uploaded_file = st.file_uploader("File တင်ပါ", type=["txt", "docx", "pdf"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".txt"):
            input_text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".docx"):
            doc = Document(uploaded_file)
            input_text = "\n".join([p.text for p in doc.paragraphs])
        elif uploaded_file.name.endswith(".pdf"):
            pdf_reader = pypdf.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    input_text += extracted + "\n"
        st.success(f"File ဖတ်ပြီးပါပြီ။ စာလုံးရေစုစုပေါင်း: {len(input_text)} characters")

# Chunking Function
def chunk_text(text, max_chars=2500):
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

# Translate Button
if st.button("Translate Now", type="primary"):
    if not api_key:
        st.error("ကျေးဇူးပြု၍ Sidebar တွင် Groq API Key ထည့်ပါ။")
    elif not input_text.strip():
        st.warning("စာသား သို့မဟုတ် File အရင်ထည့်ပါ။")
    else:
        try:
            client = Groq(api_key=api_key)
            
            chunks = chunk_text(input_text)
            translated_result = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, chunk in enumerate(chunks):
                status_text.text(f"Translating part {index + 1} of {len(chunks)}...")
                
                if src_lang == "Auto Detect":
                    prompt_content = f"Translate the following text into {target_lang}. Return ONLY the translated text without any explanation, markdown intro, or chat response:\n\n{chunk}"
                else:
                    prompt_content = f"Translate the following text from {src_lang} into {target_lang}. Return ONLY the translated text without any explanation, markdown intro, or chat response:\n\n{chunk}"
                
                response = client.chat.completions.create(
                    messages=[
                        {"role": "user", "content": prompt_content}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                translated_result.append(response.choices[0].message.content)
                progress_bar.progress((index + 1) / len(chunks))
            
            status_text.text("Translation Complete!")
            
            # Display Result
            st.subheader("ဘာသာပြန်ရလဒ် -")
            final_text = "\n\n".join(translated_result)
            st.text_area("", value=final_text, height=350)
            
            # Download Button
            st.download_button(
                label="Download Translated Text (.txt)",
                data=final_text,
                file_name="translated_result.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Error: {e}")
