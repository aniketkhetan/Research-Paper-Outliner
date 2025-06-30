def generate_outline_prompt(topic: str) -> str:
    return f"""
You are an expert research assistant helping a researcher plan a high-quality academic paper.

Your task is to generate a well-structured, formal, and hierarchical outline for a research paper on the topic:

**{topic}**

The outline should follow the structure of a standard academic research paper and must include the following top-level sections (unless the topic clearly doesn't require one):



1. Abstract  
2. Introduction  
3. Related Work  
4. Methodology  
5. Results  
6. Discussion  
7. Conclusion  
8. References

### Instructions:
- Above the Abstract Section, include a brief **Title** for the paper relative to the topic.
- Each section must include relevant **subpoints or bullet points** that guide what should be discussed in that part.
- Use a **hierarchical format** with subpoints indented clearly (e.g., numbered or bulleted).
- The output should resemble an outline used in academic writing — clear, logical, and organized.
- Avoid writing actual content — just describe what should be covered in each part.
- Be concise but informative — think of this as a planning document for the paper.
- Keep a **formal and academic tone** throughout.

### Format:
Use Markdown-style formatting with numbered sections and indented sub-bullets.

Begin the outline below:
"""
