# Resume-JD Compatibility Analyzer

Compares a candidate's resume against a job description and scores how
well they match — overall, on skills, and on years of experience — with
AI-generated resume improvement suggestions.

## Stack

- **Frontend:** React (Vite), Bootstrap 5, Axios
- **Backend:** FastAPI, Pydantic
- **NLP:** Sentence Transformers (`all-MiniLM-L6-v2`) + cosine similarity
- **LLM:** Groq API (Llama 3.3) for improvement suggestions

## How it works

1. You paste or upload (`.pdf` / `.docx` / `.txt`) a resume and a job description.
2. The backend extracts plain text from whichever format you gave it.
3. Five weighted parameters are computed and combined into the **Overall Match Score**:

   | Parameter | Weight | How it's computed |
   |---|---|---|
   | Skills Match | 30% | Curated list of ~150 tech/professional skills checked against the JD (required) vs the resume (present) |
   | Semantic Similarity | 25% | Sentence Transformer embeddings (`all-MiniLM-L6-v2`) + cosine similarity between resume and JD |
   | Experience Relevance | 20% | Years-of-experience extracted via regex from both texts and compared; detects "fresher"/entry-level self-identification |
   | Keyword Match | 15% | Dynamically extracts the JD's most frequent meaningful terms (broader net than the curated skill list) and checks resume coverage |
   | Education Match | 10% | Degree level (PhD > Master's > Bachelor's > Diploma > High school) extracted from both texts and compared |

4. The resume, JD, and all missing skills/keywords are sent to Groq's Llama
   model (`openai/gpt-oss-120b`), which returns a short list of concrete
   resume improvement suggestions.
5. Everything is returned as one JSON response and rendered on the results
   page: an overall score ring, a 5-ring breakdown with each parameter's
   weight shown, matched/missing skill and keyword pills, and the AI
   suggestions.

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Get a free Groq API key at https://console.groq.com/keys, then:

```bash
cp .env.example .env
```
and paste your key into `.env`.

```bash
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

> Note: the first analysis request will be slower (10-30s) while the
> sentence-transformer model downloads (~90MB) and loads. After that,
> requests are fast. If you don't set a Groq API key, the app still works —
> you'll just get a message in the suggestions section explaining how to
> add one, instead of AI suggestions.

### 2. Frontend

In a new terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App: http://localhost:5173

## Verified

The `/analyze` endpoint was tested end-to-end with mocked embeddings
(the real sentence-transformers model requires a large download not
available in the build environment, but its usage here — encode, then dot
product of normalized vectors — is standard). Verified: correct skills
matching (4/8 required skills → 50% skills score), correct experience
scoring (4 years vs 5 required → 80%), correct missing-skill detection,
file upload for `.txt` resumes, rejection of unsupported file types (400),
rejection of missing input (400), and the no-API-key fallback message for
suggestions. The frontend was verified to install and build with no errors.

## Project Structure

```
resume-jd-analyzer/
├── backend/
│   └── app/
│       ├── main.py
│       ├── core/config.py
│       ├── schemas/analysis.py
│       ├── routes/analyze.py
│       └── services/
│           ├── text_extraction.py    # PDF/DOCX/TXT → plain text
│           ├── embedding_service.py  # Sentence Transformers + cosine similarity
│           ├── skills_data.py        # curated skill keyword list
│           ├── keyword_service.py    # skill matching + experience-years scoring
│           └── groq_service.py       # Llama 3 suggestions via Groq
└── frontend/
    └── src/
        ├── App.jsx                   # input form → results, single page
        ├── components/
        │   ├── TextOrFileInput.jsx   # paste-or-upload toggle
        │   ├── ScoreRing.jsx         # circular score visual
        │   ├── SkillPills.jsx
        │   ├── ResultsPanel.jsx
        │   ├── Loading.jsx
        │   └── ErrorAlert.jsx
        └── services/api.js
```

## Design notes

- No authentication, database, payments, WebSockets, or RAG — matches the
  brief exactly. Each analysis is fully stateless; nothing is persisted.
- The skill list in `skills_data.py` is a static curated list, not a
  dynamic NLP extractor — kept intentionally simple per the brief. You can
  freely add more keywords to that list.
- If the Groq call fails for any reason (bad key, rate limit, network),
  the endpoint still returns the embeddings/keyword results with a
  fallback message instead of failing the whole request.
