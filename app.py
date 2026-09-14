import streamlit as st
from docx import Document
import pypdf

# Page Config
st.set_page_config(page_title="Text Splitter / Chunker", layout="wide")
st.title("✂️ စာသားနှင့် File များကို အပိုင်းလိုက် ခွဲပေးသည့် Tool")

# Initialize Session States
if "stored_text" not in st.session_state:
    st.session_state.stored_text = ""
if "chunks" not in st.session_state:
    st.session_state.chunks = []

# Input Option (Text or File Upload)
input_type = st.radio("စာသားထည့်သွင်းမည့် နည်းလမ်း ရွေးပါ -", ["Direct Text", "File Upload (.txt, .docx, .pdf)"])

if input_type == "Direct Text":
    user_input = st.text_area("ခွဲချင်သည့် စာသားများကို အောက်တွင် ထည့်ပါ -", value=st.session_state.stored_text, height=250)
    st.session_state.stored_text = user_input
else:
    uploaded_file = st.file_uploader("File တင်ပါ", type=["txt", "docx", "pdf"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".txt"):
            st.session_state.stored_text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".docx"):
            doc = Document(uploaded_file)
            st.session_state.stored_text = "\n".join([p.text for p in doc.paragraphs])
        elif uploaded_file.name.endswith(".pdf"):
            pdf_reader = pypdf.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pdf_text += extracted + "\n"
            st.session_state.stored_text = pdf_text

if st.session_state.stored_text:
    st.info(f"📊 လက်ရှိထည့်သွင်းထားသော စာလုံးရေစုစုပေါင်း: **{len(st.session_state.stored_text)}** characters")

# Splitter Options
st.subheader("⚙️ စာသား ခွဲမည့် နည်းလမ်း သတ်မှတ်ပါ")
col1, col2 = st.columns(2)

with col1:
    split_method = st.selectbox("ခွဲမည့် ပုံစံ:", ["စာလုံးရေ အလိုက် (By Characters)", "စာကြောင်းရေ အလိုက် (By Lines)"])

with col2:
    if split_method == "စာလုံးရေ အလိုက် (By Characters)":
        chunk_size = st.number_input("Part တစ်ခုလျှင် ရှိရမည့် စာလုံးရေ (Characters):", min_value=100, max_value=50000, value=3000, step=500)
    else:
        chunk_size = st.number_input("Part တစ်ခုလျှင် ရှိရမည့် စာကြောင်းရေ (Lines):", min_value=1, max_value=5000, value=50, step=10)

# Function to Split Text by Characters
def split_by_chars(text, size):
    return [text[i:i+size] for i in range(0, len(text), size)]

# Function to Split Text by Lines
def split_by_lines(text, size):
    lines = text.split("\n")
    return ["\n".join(lines[i:i+size]) for i in range(0, len(lines), size)]

# Split Action Button
if st.button("Split Text Now (စာသား အပိုင်းခွဲမည်)", type="primary"):
    current_text = st.session_state.stored_text.strip()
    
    if not current_text:
        st.warning("ကျေးဇူးပြု၍ စာသား သို့မဟုတ် File အရင်ထည့်ပါ။")
        st.session_state.chunks = []
    else:
        if split_method == "စာလုံးရေ အလိုက် (By Characters)":
            st.session_state.chunks = split_by_chars(current_text, chunk_size)
        else:
            st.session_state.chunks = split_by_lines(current_text, chunk_size)

# Display Chunks from Session State (This avoids resetting on download)
if st.session_state.chunks:
    st.success(f"စာသားများကို စုစုပေါင်း **{len(st.session_state.chunks)} အပိုင်း** (Parts) ခွဲပေးလိုက်ပါပြီ။")
    st.markdown("---")
    
    for index, chunk in enumerate(st.session_state.chunks):
        with st.expander(f"📌 Part {index + 1} (စာလုံးရေ: {len(chunk)} characters)", expanded=True):
            st.text_area(f"Part {index + 1} Content:", value=chunk, height=200, key=f"chunk_{index}")
            
            # Individual Download Button
            st.download_button(
                label=f"Download Part {index + 1} (.txt)",
                data=chunk,
                file_name=f"part_{index + 1}.txt",
                mime="text/plain",
                key=f"dl_{index}"
            )
