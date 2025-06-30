from fpdf import FPDF
import base64
import streamlit as st
import streamlit.components.v1 as components
import html
import io

def create_pdf_bytes(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)

    # Output PDF as string, encode to bytes
    pdf_output = pdf.output(dest='S').encode('latin1')
    return io.BytesIO(pdf_output)



def create_markdown_bytes(text):
    return io.BytesIO(text.encode("utf-8"))


def create_references_markdown(refs):
    lines = []
    for ref in refs:
        authors = ", ".join(a["name"] for a in ref["authors"])
        lines.append(f"- **{ref['title']}**, {authors}, *{ref['year']}*. [Link]({ref['url']})")
    return "\n".join(lines)

def create_references_md_download_button(refs, filename="references.md"):
    md_text = create_references_markdown(refs)
    return io.BytesIO(md_text.encode("utf-8"))


def copy_button(text):
    safe_text = html.escape(text)

    components.html(f"""
        <style>
            .copy-btn {{
                color: inherit;
                background: transparent;
                border: 1px solid;
                padding: 0.4em 1em;
                border-radius: 6px;
                cursor: pointer;
                font-size: inherit;
                font-weight: inherit;
                transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
            }}

            /* Dark mode */
            @media (prefers-color-scheme: dark) {{
                .copy-btn {{
                    color: #FAFAFA;
                    border-color: rgba(255, 255, 255, 0.3);
                }}
                .copy-btn:hover {{
                    border-color: #f44336;;
                    color: #f44336;
                    
                }}
                .copy-btn:active {{
                    
                    background:#f44336;
                    color: rgba(255, 255, 255, 0.8);
                    border-color: rgba(255, 0, 0, 0.8);
                }}
            }}

            /* Light mode */
            @media (prefers-color-scheme: light) {{
                .copy-btn {{
                    color: #31333F;
                    border-color: rgba(0, 0, 0, 0.2);
                }}
                .copy-btn:hover {{
                    border-color: #f44336;;
                    color: #f44336;
                    
                }}
                .copy-btn:active {{
                    
                    background:#f44336;
                    color: rgba(255, 255, 255, 0.8);
                    border-color: rgba(255, 0, 0, 0.8);
                }}
            }}
        </style>

        <textarea id="toCopy" style="display:none;">{safe_text}</textarea>
        <button class="copy-btn" onclick="copyText()">📋 Copy to Clipboard</button>

        <script>
        function copyText() {{
            var copyText = document.getElementById("toCopy");
            copyText.style.display = "block";
            copyText.select();
            document.execCommand("copy");
            copyText.style.display = "none";
            console.log("Copied!");
        }}
        </script>
    """, height=60)
