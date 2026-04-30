# Resumé Edge — AI-Powered Resume Enhancer

A full-stack web application that analyzes resumes and provides actionable AI-powered feedback covering language, structure, ATS compatibility, and impact.

**Live Demo:** [Live Demo](https://resume-enhancer-gamma.vercel.app/)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (App Router) + Tailwind CSS |
| Backend | Python + FastAPI |
| AI | Google Gemini (gemini-2.5-flash) |
| PDF Parsing | pdfplumber |
| Deployment | Vercel (frontend) + Render/Railway (backend) |

---

## Features

- **Paste or Upload** — paste resume text directly or upload a PDF (with automatic text extraction)
- **ATS Score** — compatibility score (0–100) with a visual ring indicator and explanation
- **Section-by-Section Analysis** — strengths, improvements, and rewrite examples for each section (Summary, Experience, Skills, Education, Formatting, etc.)
- **Quick Wins** — top 3–5 highest-impact changes to make immediately
- **Missing Keywords** — important industry keywords likely expected by ATS systems
- **Downloadable Report** — export the full analysis as a `.txt` file
- **Responsive Design** — works on desktop and mobile

---

## Project Structure

```
resume-enhancer/
├── backend/
│   ├── main.py           # FastAPI app with /analyze/text and /analyze/pdf endpoints
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx      # Main UI
    │   └── globals.css
    ├── components/
    │   ├── ATSScoreRing.tsx
    │   ├── SectionCard.tsx
    │   └── LoadingSkeleton.tsx
    ├── lib/api.ts        # API client functions
    ├── types/index.ts    # TypeScript types
    └── .env.local.example
```

---

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.10+
- A [Google AI / Gemini API key](https://aistudio.google.com/apikey)

### Backend

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables edit .env and add your GEMINI_API_KEY
cp .env .env

# Run the server
uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`.  
API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables, set NEXT_PUBLIC_API_URL=http://localhost:8000
cp .env.local.example .env.local

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/analyze/text` | Analyze resume from pasted text |
| POST | `/analyze/pdf` | Analyze resume from uploaded PDF |

### Example Request (text)

```bash
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "John Doe\nSoftware Engineer..."}'
```

### Example Response

```json
{
  "ats_score": 72,
  "ats_score_explanation": "Good keyword coverage but missing quantified achievements.",
  "overall_summary": "A solid resume with clear structure...",
  "sections": [
    {
      "name": "Experience",
      "status": "needs_improvement",
      "strengths": ["Clear job titles", "Relevant companies listed"],
      "improvements": ["Add quantified metrics", "Use stronger action verbs"],
      "rewritten_example": "Led migration of legacy monolith to microservices, reducing deployment time by 60%..."
    }
  ],
  "quick_wins": ["Add numbers to at least 3 bullet points", "..."],
  "keywords_missing": ["CI/CD", "Docker", "Agile"]
}
```

---

## Deployment

### Backend (Render.com — free tier)

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repo, set root to `backend/`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `GEMINI_API_KEY=your_key`

### Frontend (Vercel)

1. Import your GitHub repo on [Vercel](https://vercel.com)
2. Set root directory to `frontend/`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`
4. Deploy

---

## Design Decisions

- **Google Gemini** was chosen as the AI provider for its structured output reliability, speed, and strong instruction-following, which is critical for parsing section-by-section resume JSON.
- **pdfplumber** is used for PDF extraction as it handles multi-column layouts better than basic PDF parsers.
- **FastAPI** provides automatic OpenAPI docs, async support, and clean type-based validation.
- The frontend uses a clean, modern aesthetic (Satoshi + Inter, neutral ink palette) to feel premium and trustworthy — appropriate for a career tool.
- All AI output is returned as structured JSON, making the frontend display logic clean and predictable.
- No resume data is stored anywhere — each request is stateless.

---

## Environment Variables

### Backend (`.env`)

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key |

### Frontend (`.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | URL of the FastAPI backend |
