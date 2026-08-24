# Resume-JD Compatibility Analyzer - Backend (FastAPI)

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   The first install will also download the `sentence-transformers` model
   dependencies. The embedding model itself (~90MB) downloads automatically
   the first time you run an analysis.

3. Get a free Groq API key at https://console.groq.com/keys

4. Copy `.env.example` to `.env` and paste in your key:
   ```
   cp .env.example .env
   ```

5. Run the server:
   ```
   uvicorn app.main:app --reload
   ```

6. Open API docs at: http://127.0.0.1:8000/docs

Note: the first request will be slow (10-30s) while the sentence-transformer
model downloads and loads into memory. Subsequent requests are fast.
