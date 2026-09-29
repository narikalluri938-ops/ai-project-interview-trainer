# AI Project Interview Trainer

An AI-powered preparation platform engineered to help engineering students, B.Tech graduates, and freshers explain, defend, and master the technical projects listed on their resumes during placement interviews.

---

## 🎯 The Core Problem

Many college students put ambitious projects, algorithms, frameworks, and AI models on their resumes (e.g., FaceNet, CNNs, Microservices, Flask, MySQL, Redis) but struggle when interviewers probe with real-world technical scrutiny:
- *"Why did you choose Flask over Django or FastAPI?"*
- *"How do you handle 10,000 concurrent requests without thread exhaustion?"*
- *"Did you actually train FaceNet from scratch, or did you use pre-trained weights?"*
- *"What happens if the database crashes while writing attendance?"*

Superficial or rehearsed answers often cost students placement offers. **AI Project Interview Trainer** solves this by focusing on **understanding and defense**, rather than rote memorization.

---

## 💡 The Solution & Pedagogical Principle

The application follows an active-learning interview lifecycle:
```text
PROJECT INPUT ➔ ANTI-HALLUCINATION ANALYSIS ➔ CURATED QUESTIONS ➔
CONCEPT LEARNING ➔ ADAPTIVE MOCK INTERVIEW ➔ REAL-TIME EVALUATION ➔
FOLLOW-UP ENGINE ➔ READINESS REPORT & STUDY ORDER
```

### Key Capabilities
1. **Multi-Tier Explanations**: Generates 5 distinct spoken explanations:
   - **30-Second Elevator Pitch** (for quick introductions)
   - **1-Minute Technical Overview** (for standard interview openers)
   - **2-Minute Deep Architectural Walkthrough** (covering pipelines and trade-offs)
   - **Under-the-Hood Technical Breakdown** (data flow and mechanics)
   - **Layman Explanation** (explaining technical work to non-technical recruiters)
2. **Category-Based Questions**:
   - **Category A — Basic**: Project objectives, personal ownership, hardest bugs.
   - **Category B — Technical**: Strict match against stated tools (e.g. Python WSGI lifecycle, MySQL ACID isolation, OpenCV frame buffers).
   - **Category C — "Why Did You Choose This?"**: Defending technology choices and trade-offs objectively.
   - **Category D — Scenario & Troubleshooting**: Real-world failures (scale from 100 to 10,000 users, database crashes, lighting shifts, latency spikes).
   - **Category E — Follow-up Questions**: Probing individual contributions and detecting tutorial copy-pastes.
3. **Strict Anti-Hallucination & Resume Risk Detection**:
   - Never assumes or invents experience the student did not state.
   - Differentiates *"used pre-trained library"* from *"implemented from scratch"*.
   - Flags dangerous buzzwords and provides the exact trap questions interviewers will ask.
4. **Concept Learning Mode**:
   - Deconstructs foundational concepts into Definition, Why Used, Mechanism, Role in Project, and Interview Questions.
5. **Adaptive Mock Interview Simulator**:
   - Interactive Q&A simulation with multidimensional scoring (Clarity, Technical Correctness, Completeness, Project Relevance).
   - Dynamic difficulty adaptation: increases difficulty on strong answers, offers guidance on weak answers.
6. **Comprehensive Final Readiness Report**:
   - Readiness score gauge, strengths, areas to improve, questions struggled with, revision checklist, and prioritized study order.

---

## 🏗️ Architecture & Pluggable AI Provider

```text
project-interview-trainer/
├── app/
│   ├── __init__.py               # Flask application factory
│   ├── config.py                 # Multi-environment configuration
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── project.py            # Project entity & metadata
│   │   ├── question.py           # Question entity & categories
│   │   ├── interview.py          # Mock interview session tracker
│   │   └── answer.py             # Evaluation & follow-up record
│   ├── routes/                   # Clean Blueprints
│   │   ├── main.py               # Landing page & health check
│   │   ├── projects.py           # Project CRUD & dashboard
│   │   ├── interview.py          # Mock interview simulation & reports
│   │   └── api.py                # REST endpoints & demo data
│   ├── services/
│   │   ├── ai_providers/         # Pluggable Provider Abstraction
│   │   │   ├── base.py           # Abstract AIProvider interface
│   │   │   ├── gemini_provider.py# Google Gemini REST provider
│   │   │   ├── openai_provider.py# OpenAI API provider
│   │   │   ├── mock_provider.py  # Intelligent offline heuristic engine
│   │   │   └── factory.py        # Dynamic provider instantiator
│   │   ├── project_analyzer.py   # 5-tier explanations & risk detection
│   │   ├── question_generator.py # Curated question generation
│   │   ├── interview_evaluator.py# Multi-dimensional answer evaluation
│   │   └── report_generator.py   # Final debrief synthesis
│   ├── prompts/                  # Isolated prompt templates
│   │   ├── project_analysis.txt
│   │   ├── question_generation.txt
│   │   ├── interview_evaluation.txt
│   │   ├── followup_generation.txt
│   │   └── report_generation.txt
│   ├── templates/                # Jinja2 templates (Bootstrap 5)
│   └── static/                   # Custom CSS & interactive JS
├── tests/                        # Automated test suites (pytest)
├── requirements.txt              # Production & test dependencies
├── render.yaml                   # Infrastructure-as-code for Render
├── Procfile                      # Gunicorn deployment spec
├── pytest.ini                    # Pytest configuration
└── run.py                        # Local execution entrypoint
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, Flask, Flask-SQLAlchemy, Gunicorn
- **Database**: SQLite (local development) / PostgreSQL (production via SQLAlchemy)
- **Frontend**: HTML5, CSS3, JavaScript (ES6), Bootstrap 5, Bootstrap Icons
- **AI Engine**: Pluggable provider abstraction:
  - Google Gemini API (`gemini-2.5-flash`, `gemini-1.5-flash`)
  - OpenAI API (`gpt-4o-mini`, `gpt-4o`)
  - Smart Heuristic Provider (100% offline out-of-the-box operation)
- **Testing**: PyTest with 24 automated unit, scenario, and end-to-end acceptance tests

---

## 💻 Local Development

### Installation

1. Clone repository:
```bash
git clone https://github.com/your-username/ai-project-interview-trainer.git
cd ai-project-interview-trainer
```

2. Create virtual environment:
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

`.env` content:
```env
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production-12345
DATABASE_URL=sqlite:///instance/interview_trainer.db

# Choose: mock | gemini | openai
AI_PROVIDER=mock
AI_API_KEY=
AI_MODEL=gemini-2.5-flash
```

### Running Locally

```bash
python run.py
```
Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### Testing

Run the full automated pytest suite:
```bash
pytest -v
```

Run the live 12-step user acceptance test:
```bash
python tests/acceptance_test.py
```

Run the GitHub safety audit:
```bash
python tests/security_audit.py
```

Run the production build smoke test:
```bash
python tests/production_smoke_test.py
```

---

## 🏭 Production

### Gunicorn Command

For Linux/UNIX environments (Docker, Render, AWS, Heroku):
```bash
gunicorn run:app --workers 2 --threads 4 --timeout 120
```

*(Note: Gunicorn is a POSIX-only WSGI server and runs in Linux cloud containers. For local Windows testing, use `python run.py` with `FLASK_ENV=production` and `FLASK_DEBUG=0`).*

### Required Environment Variables

| Variable | Recommended Production Value | Description |
|---|---|---|
| `FLASK_APP` | `run.py` | Flask application entry point |
| `FLASK_ENV` | `production` | Enables production mode |
| `FLASK_DEBUG` | `0` | Strictly disables debug mode and tracebacks |
| `SECRET_KEY` | *(32+ character random hex)* | Cryptographic session signing key |
| `DATABASE_URL` | `postgresql://user:password@host:port/dbname` | Database connection string |
| `AI_PROVIDER` | `mock` or `gemini` or `openai` | Selected AI provider |
| `AI_API_KEY` | *(Optional if mock, required for Gemini/OpenAI)* | API key |
| `AI_MODEL` | `gemini-2.5-flash` or `gpt-4o-mini` | AI Model ID |

> [!WARNING]
> **Ephemeral Storage Notice:** Free cloud tiers (such as Render or Railway free instances) run on ephemeral filesystems. If you use SQLite in production, the database file will reset whenever the instance restarts or redeploys. For persistent production data, always configure `DATABASE_URL` with a managed PostgreSQL instance.

---

## 🚀 Render Deployment Step-by-Step

Follow these exact steps to deploy online:

1. **Create Account**: Sign up for a free account at [render.com](https://render.com).
2. **Connect GitHub**: Authorize Render to access your GitHub account.
3. **Create Web Service**: In the Render dashboard, click **New +** and select **Web Service**.
4. **Select Repository**: Pick your `ai-project-interview-trainer` repository.
5. **Configure Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
6. **Configure Start Command**:
   ```bash
   gunicorn run:app --workers 2 --threads 4 --timeout 120
   ```
7. **Add Environment Variables**: Under the "Environment Variables" section, add:
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `0`
   - `SECRET_KEY`: Click "Generate" to generate a secure random string
   - `AI_PROVIDER`: `mock` (or `gemini` / `openai`)
   - `AI_API_KEY`: *(Optional: leave blank for mock, or provide your Gemini key)*
   - `AI_MODEL`: `gemini-2.5-flash`
   - *(Optional for persistent database)*: Click **New +** &rarr; **PostgreSQL**, create a free PostgreSQL instance, and paste its `Internal Database URL` as `DATABASE_URL`.
8. **Deploy**: Click **Create Web Service**. Render will pull the code, install dependencies, run DB initialization, and launch the service.
9. **Verify HTTPS URL**: Once the build completes, click the provided HTTPS URL (e.g. `https://ai-project-interview-trainer.onrender.com`) and verify:
   - Landing page loads with HTTPS.
   - Click "Start Preparing" &rarr; "Fill Sample" &rarr; submit project.
   - Run a 3-question mock interview and confirm final report generation.

---

## 📸 Application Highlights

- **Landing Page**: High-converting hero section, placement problem analysis, feature cards, and sample interview simulation preview.
- **Project Form**: Streamlined form with 1-click **"Fill Sample: Face Recognition System"** button.
- **Preparation Dashboard**: Readiness percentage gauge, 5-tier explanations, architecture diagram summary, unstated assumptions, and risk alerts.
- **Curated Questions**: Filterable by Category (Basic, Technical, Why, Scenario, Follow-up) and Difficulty with collapsible interviewer tips.
- **Concept Learning Mode**: Deep dives into core mechanics, code scenarios, and likely interview questions.
- **Live Mock Interview Room**: Simulates real interviewer questions, accepts candidate answers, computes multidimensional scores, and issues dynamic follow-ups.
- **Final Interview Report**: Comprehensive readiness debrief, strengths, improvement areas, interview traps, and prioritized preparation sequence.

---

## 🔮 Future Enhancements
- Voice-based mock interview (Speech-to-Text and Text-to-Speech)
- PDF export for the Final Readiness Report
- GitHub repository automated code analysis and AST parsing
- HR and behavioral project interview mode
- Multi-project candidate portfolio comparison

---

## 📄 License
This project is open-source under the MIT License.
