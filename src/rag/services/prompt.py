prompt="""Analyze the provided image from a document page and generate a clear, highly detailed, and factual description suitable for indexing in a RAG retrieval system.

Instructions:
1. Identify the image type: Diagram, Architecture Schema, Chart/Graph, UI Screenshot, Photo, Flowchart, or Technical Drawing.
2. Extract all readable text, titles, labels, legend items, and values visible in the image.
3. Describe the main subject, structural entities, relationships, process flows, or data trends shown.
4. Keep the tone strictly objective and factual. Do not assume or hallucinate information not present in the image.
5. Do NOT include introductory phrases like "This image shows...". Output ONLY the description.
6. Provide the final response in Russian."""
