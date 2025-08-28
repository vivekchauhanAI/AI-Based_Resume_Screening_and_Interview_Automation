# AI Resume Screening Prototype

This is a minimal prototype implementing a small subset of the "AI-Based Resume Screening" system described in the uploaded spec.

Features:
- Upload resume (txt, pdf recommended)
- Basic parsing: email, phone, name heuristic
- Simple skill matching & scoring
- Mock interview slots proposal
- Audit log saved under /logs

How to run:
1. Create a Python 3.8+ virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Run backend: `python backend/app.py`
4. Open browser at http://localhost:5000/

Notes:
- PDF parsing requires PyPDF2 (optional). If not installed, PDFs may fallback to raw bytes decoding.
- This is a prototype — for production, replace heuristics with proper NLP models, add authentication, rate limiting, and full parsing libraries.
