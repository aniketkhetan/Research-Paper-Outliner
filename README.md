# Research Paper Outliner

An interactive Streamlit-based application that helps researchers generate well-structured, editable, and exportable outlines for academic research papers using large language models (LLMs).

---

##  Features

* **Prompt-Engineered LLM Generation**: Choose between Mistral and LLaMA-2 (Chat) to generate academic-style outlines.
* **Standardized Structure**: Automatically includes essential sections like Abstract, Introduction, Methodology, Results, etc.
* **Editable Interface**: Rename, edit, remove, or add custom sections via an intuitive UI.
* **Markdown Preview**: View outline in well-formatted Markdown.
* **Export Options**:

  * Copy to Clipboard
  * Download as PDF
  *  Download as Markdown
* **Reference Suggestions**: Use Semantic Scholar to fetch related papers based on the generated title (future integration).
* **Model Toggle**: Easily switch between Mistral and LLaMA-2 based on inference needs.

---

##  Technologies Used

* [Streamlit](https://streamlit.io/) - UI
* [Hugging Face Together API](https://huggingface.co/inference-api) - Model inference
* [Python FPDF](https://pyfpdf.readthedocs.io/en/latest/) - PDF Export
* [Semantic Scholar API](https://api.semanticscholar.org/) - Citation recommendations

---

##  Project Structure

```
research-paper-outliner/
├── main.py                      # Streamlit application entry
├── prompt.py                   # Prompt engineering logic
├── export_components.py        # PDF/Markdown export functions + Copy button
├── config.json                 # API token config (NOT to be uploaded)
├── requirements.txt            # Python dependencies
└── README.md                   # You're here!
```

---

##  Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/research-paper-outliner.git
cd research-paper-outliner
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add API Token

Create a `config.json` file in the root directory:

```json
{
  "HF_API_TOKEN": "your_huggingface_inference_api_key"
}
```

> ⚠️ Do NOT upload this file to GitHub or expose your token publicly.

### 5. Run the App

```bash
streamlit run main.py
```

---

## API and Model Notes

* Uses Hugging Face's **Together** router endpoint for both Mistral and LLaMA-2.
* Output parsing logic is adapted to different formatting styles:

  * `1. **Abstract**` (LLaMA-style)
  * `1. Abstract` (Mistral-style)
  * `**Title:** Paper Title Here`

---

## To-Do / Future Enhancements

* [ ] Semantic Scholar Reference Fetch & Export
* [ ] DOCX Export
* [ ] Section reordering (drag & drop)
* [ ] Rich text editing with Streamlit components
* [ ] Theming and light/dark mode support

---

## Contributing

Pull requests are welcome! Please open an issue first to discuss what you would like to change.

---

##  License

MIT License. Feel free to use, modify, and distribute.

---

##  Acknowledgements

* Hugging Face for model access
* Semantic Scholar for citation data
* Streamlit for easy UI building
