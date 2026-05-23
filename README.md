# Closira AI Customer Support Workflow
### Bloom Aesthetics Clinic

A Python CLI that simulates an AI-powered customer support agent across four stages: FAQ answering, lead qualification, escalation detection, and conversation summary. Built using the Groq API (Llama 3.1).

---

## Project Structure

```
closira-ai-workflow/
├── .env                           # Your API key (never committed to GitHub)
├── .gitignore                     # Excludes .env and venv
├── main.py                        # Main CLI application
├── sop_data.json                  # SOP source (Bloom Aesthetics Clinic)
├── prompt_design.md               # Prompt decisions and reasoning
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── test_transcripts/
│   ├── transcript1.md
│   ├── transcript2.md
│   ├── transcript3.md
│   ├── transcript4.md
│   └── transcript5.md
└── logs/                          # Auto-created at runtime; session logs saved here
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Aasrika/closira-ai-workflow.git
cd closira-ai-workflow
```

### 2. Create and activate a virtual environment

```bash
# Mac/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Create a `.env` file in the project root:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

Get a free Groq API key (no credit card required) at: https://console.groq.com

---

## Running the Workflow

```bash
python main.py
```

The CLI starts a conversation with the Bloom AI assistant. Type your messages and press Enter.

**Special commands:**
- Type `exit`, `quit`, `bye`, or `goodbye` to end the session and trigger a summary
- Booking-related keywords (e.g. "book", "appointment", "schedule") after at least one FAQ turn will trigger the lead qualification stage

---

## How It Works

### Stage 1: FAQ Answering
The AI answers questions using only the `sop_data.json` file. The full SOP is injected into the system prompt as a grounding document. The AI is explicitly prohibited from guessing or inferring facts not present in the SOP.

### Stage 2: Lead Qualification
Triggered when a customer expresses interest in booking. The AI asks 3 structured questions one at a time:
1. Which treatment are you interested in?
2. Have you had treatments before?
3. What time works best for you?

Collected data is stored as a Python dict and included in the session summary.

### Stage 3: Escalation Detection
The AI flags escalation via structured JSON output (`{"escalate": true, "reason": "...", "message": "..."}`). Escalation reasons:
- `out_of_scope` — question not answerable from SOP
- `sentiment_negative` — frustration, complaint, or anger detected
- `explicit_request` — customer asks for a human agent
- `pricing_negotiation` — customer asks for discounts or price negotiation
- `medical_question` — medical query beyond SOP scope
- `consecutive_unanswered` — 3+ out-of-scope questions in a row (Python safeguard)

### Stage 4: Conversation Summary
At session end, a structured JSON summary is generated covering:
- Customer intent
- Questions asked
- SOP gaps identified
- Lead data collected
- Escalation status and reason
- Recommended next action
- Session rating (`smooth | partial | escalated`)

Sessions are automatically saved to `logs/session_<timestamp>.json`.

---

## SOP Data

The AI operates exclusively on `sop_data.json`, which covers:

| Field | Details |
|---|---|
| Business | Bloom Aesthetics Clinic |
| Hours | Mon–Sat, 9am–7pm |
| Services | Botox (from £200), Fillers (from £250), Skin Boosters (from £300), Free Consultation |
| Booking | WhatsApp or website, 24hr cancellation policy |
| Escalation criteria | Complaints, medical questions, pricing negotiation, unanswered questions |

The SOP can be extended by editing `sop_data.json`. No code changes required.

---

## Dependencies

```
groq
python-dotenv
```

Python 3.9+ recommended.

---

## Trade-offs and Known Limitations

| Limitation | Notes |
|---|---|
| No persistent memory | Each session starts fresh. No CRM integration. |
| No streaming | Responses wait for full generation. Streaming can be added for better UX in production. |
| Sentiment detection is model-dependent | The LLM detects negative sentiment via prompt instruction. A dedicated classifier would add a safety net in production. |
| SOP is static per session | Editing `sop_data.json` requires restarting. A production system would hot-reload. |
| CLI only | No web UI or WhatsApp integration — sufficient per assignment spec. |
| Single-model architecture | All 4 stages use the same model. Production might use a lighter model for classification tasks. |

---

## API Provider Note

This project uses the **Groq API** (`llama-3.1-8b-instant`) as the LLM backend. Anthropic Claude and OpenAI both require a minimum payment or credit top-up to access their APIs, which was not feasible for this prototype. Groq provides a genuinely free tier with no credit card required, making it the most accessible option for open evaluation.

The code is fully compatible with Claude or OpenAI — swapping the provider requires changing only the API client and model name (3 lines of code).

---

## Model Used

`llama-3.1-8b-instant` via **Groq API**

Groq was chosen for its free tier (no credit card required), fast inference speed, and strong instruction-following capability in Llama 3.1, which handles structured JSON output and system prompt grounding reliably.
