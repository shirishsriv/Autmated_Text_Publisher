# 📘 Book Chapter Scraper & Text Sanitizer

This is a Flask-based web application that allows users to scrape book chapters from public sources (like Wikisource), clean or rewrite them using **Google Gemini AI**, and archive the processed content using **ChromaDB** for future reference.

---

## 🚀 Features

- 🔗 **Scrape Chapter**  
  Input a chapter URL (e.g., from Wikisource) to extract and display raw content.

- ✍️ **Sanitize & Rewrite**  
  Use Google Gemini AI to clean, format, or rewrite the scraped chapter with optional custom instructions.

- 💾 **Archive Sanitized Text**  
  Store cleaned chapters in **ChromaDB** with associated metadata.

- 📂 **View Archive**  
  Browse all previously archived and AI-enhanced chapters in an organized interface.

---

## 🛠️ Tech Stack

| Layer        | Technology                |
|--------------|---------------------------|
| Backend      | Flask, Playwright         |
| AI Model     | Google Gemini (via `google.generativeai`) |
| Vector DB    | ChromaDB                  |
| Frontend     | HTML, CSS (Bootstrap)     |

---

## 📦 Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/book-chapter-sanitizer.git
   cd book-chapter-sanitizer

## Installation dependencies
* Ensure you have Python 3.8+ and Playwright installed.
* pip install -r requirements.txt
* playwright install

## Set Environment Variable
* You'll need an API key from Google AI Studio for Gemini:
* export GOOGLE_API_KEY="your-google-api-key"
* You can add this to your .bashrc, .zshrc, or .env file for persistence.

##  Running the App
* python app.py
* Visit http://localhost:5000 in your browser.

## 🧪 Project Structure
📁 project/
│
├── app.py                 # Main Flask application
├── chroma_db/             # ChromaDB persistent vector store
├── templates/
│   ├── index.html         # Main interface
│   └── archive.html       # Archived chapters display
├── static/                # (Optional for CSS or images)
└── requirements.txt       # Python dependencies

## 📚 Example Use Case
* Input: https://en.wikisource.org/wiki/Example_Book_Chapter

* Instruction: Summarize and remove outdated language.

* Output: AI-sanitized version stored in ChromaDB with title metadata.

* Access archived entries from the "📂 View Archived Chapters" section.

## 🧠 Gemini AI Usage Note
* This project uses Google's Gemini 1.5 Flash model for fast and efficient content rewriting. Make sure your Google API key has access to this model via Google AI Studio.

## 🗂️ Dependencies
* Flask

* Playwright

* ChromaDB

* google-generativeai

* dotenv (optional for env vars)

## 📄 License
* MIT License. Free to use and adapt for educational and personal purposes.

## Future Enhancements
* Add authentication to protect archives

* Support more data sources (e.g., PDFs, EPUBs)

* Add export to PDF/Markdown

* Integrate Gemini Pro for more detailed rewrites

## 🙋‍♂️ Author

### Shirish Srivastava
Feel free to reach out or contribute!







