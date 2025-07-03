import streamlit as st
import requests
import os
import json
import re
from collections import OrderedDict
from prompt import generate_outline_prompt
from export_components import create_pdf_bytes, create_markdown_bytes, copy_button

# Load config
with open("config.json") as f:
    config = json.load(f)

HF_API_TOKEN = config["HF_API_TOKEN"]

def query_llm(prompt: str, model_choice: str):
    model_id = {
        "Mistral": "mistralai/Mistral-7B-Instruct-v0.3",
        "LLaMA-2 (Chat)": "meta-llama/Llama-3.2-3B-Instruct-Turbo"
    }.get(model_choice, "mistralai/Mistral-7B-Instruct-v0.3")

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post("https://router.huggingface.co/together/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error {response.status_code}: {response.text}"

def normalize_to_markdown(text):
    lines = text.splitlines()
    markdownified = []
    title_found = False
    for line in lines:
        if not title_found and (line.strip().lower().startswith("**title:**") or line.strip().lower().startswith("title:")):
            title = re.sub(r"(?i)^\*?\*?title:?\*?\*?", "", line).strip()
            markdownified.append(f"# Title\n{title}\n")
            title_found = True
        elif re.match(r"^\d+\.\s+\*\*(.*?)\*\*", line):
            heading = re.findall(r"\*\*(.*?)\*\*", line)[0]
            markdownified.append(f"# {heading}")
        elif re.match(r"^\d+\.\s+", line):
            heading = line.split(". ", 1)[-1].strip()
            markdownified.append(f"# {heading}")
        else:
            markdownified.append(line)
    return "\n".join(markdownified)

def parse_outline_to_dict(markdown_text):
    if not markdown_text.strip().startswith("#"):
        markdown_text = normalize_to_markdown(markdown_text)

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

st.subheader("🤖 Choose a Model")
model_choice = st.selectbox("Select an LLM", ["Mistral", "LLaMA-2 (Chat)"])

# Generate outline
generate_clicked = st.button("🚀 Generate Outline")
if generate_clicked and topic.strip():
    with st.spinner("Generating structured outline..."):
        prompt = generate_outline_prompt(topic, model=model_choice)
        outline = query_llm(prompt, model_choice)
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

    if st.button("✅ Done Editing"):
        st.session_state.edit_mode = False
