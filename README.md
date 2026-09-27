cat > README.md << 'EOF'
# AI Incident Root Cause Analyzer (FastAPI + SQLite + PDF)

AI-powered incident triage backend that analyzes **logs**, **stack traces**, and **metrics** to produce:
- Probable root cause
- Affected services
- Severity classification
- Fix recommendation
- Post-mortem summary
- Downloadable PDF incident report

> Includes a resilient fallback mode so the API remains demoable even when LLM quota is unavailable.

## Tech Stack
FastAPI • OpenAI (optional) • SQLite • ReportLab (PDF)

## Run Locally
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export OPENAI_API_KEY="YOUR_KEY"   # optional (fallback works without it)
export OPENAI_MODEL="gpt-4o-mini"
uvicorn main:app --reload --port 8000
