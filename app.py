import streamlit as st
from deep_translator import GoogleTranslator
from docx import Document
import pypdf

# Page Config
st.set_page_config(page_title="Free Unlimited Translator", layout="wide")
st.title("🌐 Free Unlimited Translator (API Key မလိုပါ)")

# Language Mapping Dictionary
LANG_MAP = {
    "Auto Detect": "auto",
    "Burmese (Myanmar)": "my",
    "English": "en",
    "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW",
    "Japanese": "ja",
    "Korean": "ko",
    "Thai": "th",
    "Vietnamese": "vi",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Russian": "ru",
    "Hindi": "hi",
    "Bengali": "bn",
    "Indonesian": "id",
    "Malay": "ms",
    "Filipino": "tl",
    "Italian": "it",
    "Portuguese": "pt",
    "Arabic": "ar",
    "Turkish": "tr"
}

lang_names = list(LANG_MAP.keys())

# Select Languages
col1, col2 = st.columns(2)
with col1:
    src_lang_name = st.selectbox("From (မူရင်းဘာသာစကား):", lang_names)
with col2:
    target_lang_name = st.selectbox("To (ပြန်ဆိုချင်သည့်ဘာသာစကား):", lang_names[1:], index=0) # Default Burmese

src_code = LANG_MAP[src_lang_name]
target_code = LANG_MAP[target_lang_name]

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

# Chunking Function (4000-char အပိုင်းများ ခွဲခြင်း)
def chunk_text(text, max_chars=4000):
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

# Translate Button
if st.button("Translate Now", type="primary"):
    if not input_text.strip():
        st.warning("စာသား သို့မဟုတ် File အရင်ထည့်ပါ။")
    else:
        try:
            translator = GoogleTranslator(source=src_code, target=target_code)
            
            chunks = chunk_text(input_text)
            translated_result = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, chunk in enumerate(chunks):
                status_text.text(f"Translating part {index + 1} of {len(chunks)}...")
                
                # Free Google Translate Call
                translated_chunk = translator.translate(chunk)
                translated_result.append(translated_chunk)
                
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
