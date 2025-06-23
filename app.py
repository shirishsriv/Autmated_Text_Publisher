from flask import Flask, render_template, request
from playwright.sync_api import sync_playwright
import os
import re
import chromadb
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")  # Or "gemini-pro", based on your access

# Setup ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("sanitized_chapters")

# Utility to sanitize filenames
def sanitize_filename(title):
    return re.sub(r'[^a-zA-Z0-9_\- ]+', '', title).replace(" ", "_")

# Scrape chapter content
def scrape_chapter_to_file(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector('#mw-content-text')

        title = page.query_selector('#firstHeading').inner_text()
        content_element = page.query_selector('#mw-content-text .mw-parser-output')
        paragraphs = content_element.query_selector_all("p")
        content = "\n\n".join([p.inner_text().strip() for p in paragraphs if p.inner_text().strip()])
        browser.close()

        filename = sanitize_filename(title) + ".txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{title}\n\n{content}")
        return filename, title, content

# Sanitize with Gemini
def sanitize_with_gemini(raw_text, instruction):
    prompt = f"{instruction}\n\n{raw_text}"
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

# Home route
@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    raw_text = ""
    cleaned_text = ""
    title = ""

    if request.method == "POST":
        if "chapter_url" in request.form:
            try:
                filename, title, raw_text = scrape_chapter_to_file(request.form.get("chapter_url"))
                message = f"✅ Chapter saved as '{filename}'"
            except Exception as e:
                message = f"❌ Error scraping: {str(e)}"

        elif "sanitize" in request.form:
            try:
                raw_text = request.form.get("raw_text")
                title = request.form.get("title", "Unknown Chapter")
                user_prompt = request.form.get("edit_instruction", "Clean and sanitize the chapter.")
                cleaned_text = sanitize_with_gemini(raw_text, user_prompt)
                message = "✅ Text sanitized. You can now archive it."
            except Exception as e:
                message = f"❌ Error during sanitization: {str(e)}"

        elif "archive" in request.form:
            try:
                title = request.form.get("title", "Untitled")
                cleaned_text = request.form.get("cleaned_text")
                doc_id = sanitize_filename(title)
                collection.add(
                    documents=[cleaned_text],
                    metadatas=[{"title": title}],
                    ids=[doc_id]
                )
                message = f"✅ Text archived to ChromaDB with ID '{doc_id}'"
            except Exception as e:
                message = f"❌ Error archiving to ChromaDB: {str(e)}"

    return render_template("index.html", message=message, raw_text=raw_text, cleaned_text=cleaned_text, title=title)

# Archive view route
@app.route("/archive", methods=["GET"])
def archive():
    try:
        documents = collection.get(include=["documents", "metadatas"])
        docs = [
            {"document": doc, "metadata": meta}
            for doc, meta in zip(documents["documents"], documents["metadatas"])
        ]
    except Exception as e:
        docs = []
    return render_template("archive.html", documents=docs)

if __name__ == "__main__":
    app.run(debug=True)
