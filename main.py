import streamlit as st
import requests
import os
import json
from collections import OrderedDict
from prompt import generate_outline_prompt
from export_components import create_pdf_bytes,create_markdown_bytes,copy_button, create_references_md_download_button

# Load config
with open("config.json") as f:
    config = json.load(f)

HF_API_TOKEN = config["HF_API_TOKEN"]
API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.3"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def query_llm(prompt: str):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 1024, "return_full_text": False}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result[0]["generated_text"]
    else:
        return f"❌ Error {response.status_code}: {response.text}"

def parse_outline_to_dict(markdown_text):
    sections = OrderedDict()
    current_section = None
    current_content = []
    for line in markdown_text.strip().split("\n"):
        line = line.strip()
        if line.startswith("#"):
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line.lstrip("#").strip()
            current_content = []
        else:
            current_content.append(line)
    if current_section:
        sections[current_section] = "\n".join(current_content).strip()
    return sections

def rebuild_outline_from_sections(sections_dict):
    outline = ""
    for section, content in sections_dict.items():
        clean_section = section or "Untitled Section"
        clean_content = content or ""
        outline += f"# {clean_section}\n{clean_content.strip()}\n\n"
    return outline.strip()

def fetch_references_from_semantic_scholar(title, limit=5):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": title,
        "limit": limit,
        "fields": "title,authors,year,url"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# ---------- Streamlit UI ----------
st.set_page_config(page_title="🧠 Research Paper Outliner", layout="centered")
st.markdown("<h1 style='text-align: center;'>📄 Research Paper Outliner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Generate a structured academic outline using an LLM</p>", unsafe_allow_html=True)
st.markdown("---")

# Initialize session state
if "custom_sections" not in st.session_state:
    st.session_state.custom_sections = OrderedDict()
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# Input form
st.subheader("📝 Enter Your Research Topic")
topic = st.text_area("Topic", placeholder="e.g., Applications of Transformers in Biomedical NLP", height=100)
generate_clicked = st.button("🚀 Generate Outline")

# Generate outline
if generate_clicked and topic.strip():
    with st.spinner("Generating structured outline..."):
        prompt = generate_outline_prompt(topic)
        outline = query_llm(prompt)
        if outline.startswith("```") or outline.startswith("~~~"):
            outline = outline.strip("```").strip("~~~")
        st.session_state.custom_sections = parse_outline_to_dict(outline)
        st.session_state.edit_mode = False
        st.success("✅ Outline generated!")

# DISPLAY MODE
if st.session_state.custom_sections and not st.session_state.edit_mode:
    final_outline = rebuild_outline_from_sections(st.session_state.custom_sections)
    st.markdown("---")

    with st.container():
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown("### 📑 Outline Preview")
        with col2:
            if st.button("✏️ Edit", key="edit_outline", help="Edit the outline"):
                st.session_state.edit_mode = True

    st.markdown(final_outline)

    col1, col2, col3 = st.columns(3)
    pdf_bytes = create_pdf_bytes(final_outline)
    md_bytes = create_markdown_bytes(final_outline)
    with col1:
       copy_button(final_outline)
    with col2:
        
        st.download_button(
            label="📥 Download as PDF",
            data=pdf_bytes,
            file_name="outline.pdf",
            mime="application/pdf"
        )
    with col3:
        st.download_button(
            label="📄 Download as Markdown",
            data=md_bytes,
            file_name="outline.md",
            mime="text/markdown"
        )


# EDIT MODE
elif st.session_state.edit_mode:
    st.markdown("---")
    st.subheader("🧩 Customize Your Outline Sections")

    edited_sections = list(st.session_state.custom_sections.keys())
    pending_renames = {}
    updated_contents = {}

    for section in edited_sections:
        with st.expander(f"✏️ {section}", expanded=False):
            col1, col2 = st.columns([4, 1])
            with col1:
                new_name = st.text_input("Section Name", value=section, key=f"name_{section}")
            with col2:
                if new_name != section and st.button("Rename", key=f"rename_{section}"):
                    pending_renames[section] = new_name

            if st.button("🗑️ Remove", key=f"remove_{section}"):
                st.session_state.custom_sections.pop(section)
                continue

            updated_notes = st.text_area("Section Notes", value=st.session_state.custom_sections.get(section, ""), key=f"notes_{section}")
            updated_contents[section] = updated_notes

    # Apply content edits
    for section, notes in updated_contents.items():
        if section in st.session_state.custom_sections:
            st.session_state.custom_sections[section] = notes

    # Apply renames in-place preserving order
    if pending_renames:
        new_ordered = OrderedDict()
        for old_name in edited_sections:
            if old_name in pending_renames:
                new_name = pending_renames[old_name]
                new_ordered[new_name] = st.session_state.custom_sections.pop(old_name)
            elif old_name in st.session_state.custom_sections:
                new_ordered[old_name] = st.session_state.custom_sections[old_name]
        st.session_state.custom_sections = new_ordered

    # Add new section
    with st.expander("➕ Add New Section"):
        new_section = st.text_input("Section Title", key="new_sec_title")
        new_notes = st.text_area("Section Notes", key="new_sec_notes")
        if st.button("Add Section"):
            if new_section.strip():
                st.session_state.custom_sections[new_section.strip()] = new_notes.strip()
            else:
                st.warning("Please provide a valid section title.")

    updated_outline = rebuild_outline_from_sections(st.session_state.custom_sections)
    st.markdown("### 🧾 Updated Outline Preview")
    st.markdown(updated_outline)
    # col1, col2, col3 = st.columns(3)
    # pdf_bytes = create_pdf_bytes(updated_outline)
    # md_bytes = create_markdown_bytes(updated_outline)
    # with col1:
    #    copy_button(updated_outline)
    # with col2:
        
    #     st.download_button(
    #         label="📥 Download as PDF",
    #         data=pdf_bytes,
    #         file_name="outline.pdf",
    #         mime="application/pdf"
    #     )
    # with col3:
    #     st.download_button(
    #         label="📄 Download as Markdown",
    #         data=md_bytes,
    #         file_name="outline.md",
    #         mime="text/markdown"
    #     )

    if st.button("✅ Done Editing"):
        st.session_state.edit_mode = False
