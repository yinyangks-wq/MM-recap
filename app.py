import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="Unlimited Translator", layout="wide")
st.title("🌐 စာလုံးရေ အကန့်အသတ်မရှိ ဘာသာပြန် App")

# Sidebar - API Key input
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

# Select Languages
col1, col2 = st.columns(2)
with col1:
    src_lang = st.selectbox("From:", ["English", "Myanmar", "Japanese", "Chinese", "Korean"])
with col2:
    target_lang = st.selectbox("To:", ["Myanmar", "English", "Japanese", "Chinese", "Korean"])

# Text input
input_text = st.text_area("ဘာသာပြန်ချင်သည့် စာသားများကို အောက်တွင် ထည့်ပါ -", height=250)

# Chunking Function (စာလုံးအရှည်ကြီးကို ပိုင်းဖြတ်ပေးသည့် စနစ်)
def chunk_text(text, max_chars=3000):
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

# Translate Button
if st.button("Translate", type="primary"):
    if not api_key:
        st.error("ကျေးဇူးပြု၍ Sidebar တွင် Gemini API Key ထည့်ပါ။")
    elif not input_text.strip():
        st.warning("စာသား အရင်ရိုက်ထည့်ပါ။")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Divide into chunks for unlimited text processing
            chunks = chunk_text(input_text)
            translated_result = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, chunk in enumerate(chunks):
                status_text.text(f"Translating part {index + 1} of {len(chunks)}...")
                
                prompt = f"Translate the following text from {src_lang} to {target_lang}. Preserve the original context and formatting:\n\n{chunk}"
                
                response = model.generate_content(prompt)
                translated_result.append(response.text)
                
                # Update Progress
                progress_bar.progress((index + 1) / len(chunks))
            
            status_text.text("Translation Complete!")
            
            # Display Result
            st.subheader("ဘာသာပြန်ရလဒ် -")
            final_text = "\n\n".join(translated_result)
            st.text_area("", value=final_text, height=300)
            
            # Download Button
            st.download_button("Download Translated Text", final_text, file_name="translated_text.txt")
            
        except Exception as e:
            st.error(f"Error: {e}")
