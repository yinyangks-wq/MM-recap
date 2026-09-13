import streamlit as st
from docx import Document
import pypdf

# Page Config
st.set_page_config(page_title="Text Splitter / Chunker", layout="wide")
st.title("✂️ စာသားနှင့် File များကို အပိုင်းလိုက် ခွဲပေးသည့် Tool")

# Input Option (Text or File Upload)
input_type = st.radio("စာသားထည့်သွင်းမည့် နည်းလမ်း ရွေးပါ -", ["Direct Text", "File Upload (.txt, .docx, .pdf)"])

input_text = ""

if input_type == "Direct Text":
    input_text = st.text_area("ခွဲချင်သည့် စာသားများကို အောက်တွင် ထည့်ပါ -", height=250)
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

# Splitter Options
st.subheader("⚙️ စာသား ခွဲမည့် နည်းလမ်း သတ်မှတ်ပါ")
col1, col2 = st.columns(2)

with col1:
    split_method = st.selectbox("ခွဲမည့် ပုံစံ:", ["စာလုံးရေ အလိုက် (By Characters)", "စာကြောင်းရေ အလိုက် (By Lines)"])

with col2:
    if split_method == "စာလုံးရေ အလိုက် (By Characters)":
        chunk_size = st.number_input("Part တစ်ခုလျှင် ရှိရမည့် စာလုံးရေ (Characters):", min_value=100, max_value=50000, value=3000, step=500)
    else:
        chunk_size = st.number_input("Part တစ်ခုလျှင် ရှိရမည့် စာကြောင်းရေ (Lines):", min_value=5, max_value=5000, value=50, step=10)

# Function to Split Text by Characters
def split_by_chars(text, size):
    return [text[i:i+size] for i in range(0, len(text), size)]

# Function to Split Text by Lines
def split_by_lines(text, size):
    lines = text.split("\n")
    return ["\n".join(lines[i:i+size]) for i in range(0, len(lines), size)]

# Split Action
if st.button("Split Text Now (စာသား အပိုင်းခွဲမည်)", type="primary"):
    if not input_text.strip():
        st.warning("ကျေးဇူးပြု၍ စာသား သို့မဟုတ် File အရင်ထည့်ပါ။")
    else:
        if split_method == "စာလုံးရေ အလိုက် (By Characters)":
            chunks = split_by_chars(input_text, chunk_size)
        else:
            chunks = split_by_lines(input_text, chunk_size)
        
        st.success(f"စာသားများကို စုစုပေါင်း **{len(chunks)} ရာ** (Parts) ခွဲပေးလိုက်ပါပြီ။")
        st.markdown("---")
        
        # Display Result Chunks
        for index, chunk in enumerate(chunks):
            with st.expander(f"📌 Part {index + 1} (စာလုံးရေ: {len(chunk)} characters)", expanded=(index == 0)):
                st.text_area(f"Part {index + 1} Content:", value=chunk, height=200, key=f"chunk_{index}")
                
                # Individual Download Button
                st.download_button(
                    label=f"Download Part {index + 1} (.txt)",
                    data=chunk,
                    file_name=f"part_{index + 1}.txt",
                    mime="text/plain",
                    key=f"dl_{index}"
                )
