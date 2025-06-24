from flask import Flask, render_template, request, redirect, url_for
from playwright.sync_api import sync_playwright
import os
import re
import chromadb
from chromadb.config import Settings
import google.generativeai as genai

app = Flask(__name__)

# Set up Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("sanitized_chapters")

# Sanitize file names
def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\- ]+', '', name).replace(" ", "_")

# Scrape content from a URL
def scrape_chapter_to_file(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector('#mw-content-text')

        title = page.query_selector('#firstHeading').inner_text()
        content_element = page.query_selector('#mw-content-text .mw-parser-output')
        paragraphs = content_element.query_selector_all("p")
        content = "\n\n".join([p.inner_text().strip() for p in paragraphs if p.inner_text().strip() != ""])
        browser.close()

        filename = sanitize_filename(title) + ".txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{title}\n\n{content}")
        return filename, title, content

# Use Gemini to sanitize text
def sanitize_with_gemini(raw_text, instruction):
    prompt = f"{instruction}\n\n{raw_text}"
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

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
                title = request.form.get("title", "Untitled Chapter")
                user_prompt = request.form.get("edit_instruction", "Clean and sanitize the chapter.")

                cleaned_text = sanitize_with_gemini(raw_text, user_prompt)
                message = "✅ Text sanitized successfully."

            except Exception as e:
                message = f"❌ Error sanitizing text: {str(e)}"

        elif "archive" in request.form:
            try:
                cleaned_text = request.form.get("cleaned_text")
                title = request.form.get("title", "Untitled Chapter")
                filename_input = request.form.get("filename")

                # Determine ID
                doc_id = sanitize_filename(filename_input) if filename_input else sanitize_filename(title)

                # Save to ChromaDB
                collection.add(
                    documents=[cleaned_text],
                    metadatas=[{"title": title}],
                    ids=[doc_id]
                )

                # Save to local archive
                os.makedirs("archive", exist_ok=True)
                file_path = os.path.join("archive", doc_id + ".txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"{title}\n\n{cleaned_text}")

                message = f"✅ Text archived with ID '{doc_id}' and saved locally."

            except Exception as e:
                message = f"❌ Error archiving text: {str(e)}"

    return render_template("index.html", message=message, raw_text=raw_text, cleaned_text=cleaned_text, title=title)

@app.route("/archive", methods=["GET"])
def archive():
    try:
        results = collection.get(include=["documents", "metadatas"])
        documents = [{"document": d, "metadata": m} for d, m in zip(results["documents"], results["metadatas"])]
        return render_template("archive.html", documents=documents)
    except Exception as e:
        return f"❌ Error loading archive: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)

