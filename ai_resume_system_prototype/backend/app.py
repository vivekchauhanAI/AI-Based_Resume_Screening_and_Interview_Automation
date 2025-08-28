from flask import Flask, request, jsonify, send_from_directory
import re, os, io, datetime, json
try:
    import PyPDF2
except Exception:
    PyPDF2 = None

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

SKILLS = ["python","machine learning","aws","kubernetes","docker","sql","nlp","pytorch","tensorflow","java","c++","react","aws","azure","leadership","communication"]

def extract_text_from_pdf(file_stream):
    if not PyPDF2:
        return ""
    try:
        reader = PyPDF2.PdfReader(file_stream)
        text = []
        for p in reader.pages:
            text.append(p.extract_text() or "")
        return "\n".join(text)
    except Exception as e:
        return ""

def parse_basic(text):
    out = {}
    # email
    m = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    out['email'] = m.group(0) if m else None
    # phone (simplified)
    m = re.search(r"(?:\+\d{1,3}[\s-])?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}", text)
    out['phone'] = m.group(0) if m else None
    # name heuristic: first non-empty line not containing email/phone or common words
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = None
    for ln in lines[:10]:
        if out['email'] and out['email'] in ln: 
            continue
        if out['phone'] and out['phone'] in ln:
            continue
        if len(ln.split())<=6 and any(c.isalpha() for c in ln) and not any(k in ln.lower() for k in ['resume','curriculum','objective','email','phone','address']):
            name = ln
            break
    out['name'] = name
    # experience years heuristic: look for "X years" or "X+ years"
    m = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)", text, re.IGNORECASE)
    out['experience_years'] = float(m.group(1)) if m else None
    # skills matching
    text_low = text.lower()
    matched = []
    for s in SKILLS:
        if s.lower() in text_low:
            matched.append(s)
    out['skills'] = matched
    return out

def score_candidate(parsed):
    # simple weighted score: skills match weight 0.7, experience weight 0.3
    skill_score = min(1.0, len(parsed.get('skills',[])) / 5.0)
    exp = parsed.get('experience_years') or 0.0
    exp_score = min(1.0, exp / 10.0)
    overall = 0.7 * skill_score + 0.3 * exp_score
    return round(overall, 4), {'skill_score': round(skill_score,4), 'experience_score': round(exp_score,4)}

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('resume')
    if not f:
        return jsonify({'error':'no file uploaded'}), 400
    filename = f.filename.lower()
    text = ""
    if filename.endswith('.txt'):
        text = f.read().decode(errors='ignore')
    elif filename.endswith('.pdf'):
        text = extract_text_from_pdf(f.stream) or f.read().decode(errors='ignore')
    else:
        # try to read as text
        try:
            text = f.read().decode(errors='ignore')
        except:
            text = ""
    parsed = parse_basic(text)
    score, breakdown = score_candidate(parsed)
    summary = "\n".join([ln for ln in text.splitlines() if ln.strip()][:3]) or (", ".join(parsed.get('skills',[])) or "No textual summary available")
    # mock interview slots (next 3 business days at 10:00)
    slots = []
    today = datetime.date.today()
    added = 0
    d = today
    while added < 3:
        d = d + datetime.timedelta(days=1)
        if d.weekday() < 5:
            slots.append({
                "datetime": datetime.datetime.combine(d, datetime.time(hour=10)).isoformat() + "Z",
                "duration_minutes": 45
            })
            added += 1
    result = {
        "application_id": "APP-" + datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "candidate_profile": {
            "parsed_data": parsed,
            "parsing_confidence": 0.8
        },
        "ranking_result": {
            "overall_score": score,
            "scoring_breakdown": breakdown
        },
        "ai_summary": {
            "executive_summary": summary
        },
        "interview_scheduling": {
            "status": "slots_proposed",
            "proposed_slots": slots
        },
        "audit_trail": {
            "processing_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "model_version": "prototype-v0.1"
        }
    }
    # save audit log
    os.makedirs('logs', exist_ok=True)
    with open(os.path.join('logs', result['application_id'] + '.json'),'w') as fh:
        json.dump(result, fh, indent=2)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
