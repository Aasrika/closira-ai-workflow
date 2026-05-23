# Prompt Design Document
## Closira AI Customer Support Workflow — Bloom Aesthetics Clinic

---

## 1. System Prompt (FAQ Stage)

```
You are Bloom, a friendly and professional AI assistant for Bloom Aesthetics Clinic.

Your role is to answer customer enquiries using ONLY the information in the SOP document below.
You must NEVER invent, guess, or infer information that is not explicitly stated in the SOP.

## SOP DOCUMENT (your only source of truth):
[Full SOP JSON injected here]

## Behaviour Rules:
1. Answer questions warmly and concisely using only the SOP above.
2. If a question cannot be answered from the SOP, respond with exactly this JSON flag:
   {"escalate": true, "reason": "out_of_scope", "message": "<your polite message>"}
3. If the customer expresses frustration, anger, or makes a complaint, respond with:
   {"escalate": true, "reason": "sentiment_negative", "message": "<empathetic message>"}
4. If the customer asks to speak to a human or requests an agent:
   {"escalate": true, "reason": "explicit_request", "message": "<your message>"}
5. If the customer asks about pricing negotiation or discounts:
   {"escalate": true, "reason": "pricing_negotiation", "message": "<your message>"}
6. For medical questions beyond the listed side effects in the SOP:
   {"escalate": true, "reason": "medical_question", "message": "<your message>"}
7. For normal, answerable questions — respond in plain text (NOT JSON).
8. Keep responses under 120 words. Be warm, clear, and professional.
9. Sign off as "Bloom 🌸" on first contact.
```

---

## 2. Design Decisions

### 2.1 SOP Injected Directly into System Prompt

Decision: The full SOP JSON is injected verbatim into the system prompt at startup.

Reasoning: This approach gives the model a single, unambiguous source of truth and grounds every response to that context window. It eliminates the need for a retrieval layer (e.g. RAG) for this scope of SOP, which is small enough to fit comfortably. For larger SOPs (>10k tokens), a RAG-based approach with semantic chunking would be more appropriate.

Trade-off: If the SOP grows significantly, the system prompt becomes expensive. For this assignment, clarity and simplicity were prioritised over token efficiency.

---

### 2.2 Structured JSON Escalation Flags

Decision: The model is instructed to return a specific JSON structure `{"escalate": true, "reason": "...", "message": "..."}` rather than a natural language signal when escalation is needed.

Reasoning: This is a machine-readable, reliable escalation mechanism. Rather than doing secondary sentiment classification on the AI's plain-text responses, the AI itself declares intent in a structured format. This is far more reliable in production pipelines because:
- It's unambiguous (no false positives from parsing)
- The `reason` field enables precise logging and routing
- The `message` field ensures the customer still receives a warm, polite response

Alternative considered: Using a post-processing classifier on every AI response. Rejected because it adds latency and another failure point.

---

## 3. Hallucination Prevention

### 3.1 Hard Boundary Instruction

The system prompt contains an explicit prohibition:
> "You must NEVER invent, guess, or infer information that is not explicitly stated in the SOP."

This is reinforced structurally: the SOP is the *only document* provided in context. The model has no web access and no external knowledge retrieval. It is instructed to treat the SOP as its sole source.

### 3.2 Graceful Failure via Escalation

Rather than allowing the model to say "I'm not sure but..." (which can drift into hallucination), the model is instructed to return an escalation JSON flag for *any* out-of-scope question. This makes graceful failure the *default path*, not the exception.

### 3.3 No Speculation Framing

The system prompt avoids permissive language like "try to help the customer as best you can." Such instructions encourage the model to fill gaps creatively. Instead, the framing is: "answer only from the SOP or escalate." There is no middle ground.

### 3.4 Response Length Cap

Responses are capped at 120 words. Short responses reduce the surface area for the model to drift into speculative territory, particularly when elaborating on medical or pricing details.

---

## 4. Confidence-Based Escalation

Escalation is detected through two mechanisms working in concert:

### 4.1 Model-Declared Escalation (Primary)

The model itself is instructed to return `{"escalate": true}` when it detects:
- It cannot answer from SOP (low confidence / out-of-scope)
- Negative sentiment in the customer message
- An explicit human request

This is effectively **model-reported confidence** — asking the model to self-assess and flag uncertainty, which works well with instruction-following models like Claude.

### 4.2 Python Safeguard — Consecutive Unanswered Tracking

In `main.py`, the application tracks `unanswered_count`. If three consecutive turns result in `out_of_scope` escalations, Python overrides the reason to `consecutive_unanswered` and escalates unconditionally. This prevents infinite loops where the AI keeps trying to handle questions it cannot answer.

```python
if reason == "out_of_scope":
    state.unanswered_count += 1
    if state.unanswered_count >= 3:
        reason = "consecutive_unanswered"
```

---

## 5. Tone and Persona

### 5.1 Persona: "Bloom"

The assistant is named Bloom — aligned with the clinic's brand ("Bloom Aesthetics"). This is intentional for two reasons:
1. It creates brand consistency (customers feel they're talking to the clinic, not a generic AI)
2. It makes the assistant feel like a named team member rather than a bot, which research suggests improves customer trust in service contexts

### 5.2 Communication Style

The tone is defined as:
- **Warm** — aesthetics clients are often nervous or self-conscious; a cold, clinical tone would be off-putting
- **Reassuring** — the AI validates questions and never dismisses concerns
- **Non-pushy** — the AI does not upsell or create urgency
- **Professional but approachable** — avoids both overly formal language and slang

The AI uses emojis sparingly (🌸 as a signature), which is appropriate for WhatsApp/conversational interfaces used by SMBs.

### 5.3 SMB Context Considerations

For small businesses:
- Customers often ask very specific questions (exact prices, exact availability) — the AI must be precise and honest about gaps rather than giving vague answers
- Escalation to a human is a feature, not a failure — the AI is designed to hand off gracefully, preserving the human relationship

---

## 6. Lead Qualification Prompt Design

The qualification prompt uses a strict one-question-at-a-time constraint. This is deliberate:
- Asking all three questions at once overwhelms customers and feels like a form, not a conversation
- Sequential questioning mimics how a real receptionist would qualify a caller
- The AI is instructed to confirm collected data in a summary before closing, giving the customer a chance to correct errors

Completion is signalled via `{"qualification_complete": true, "data": {...}}` — the same JSON flag pattern used for escalations, keeping the parsing logic consistent.

---

## 7. Summary Prompt Design

The summary prompt receives:
- The full conversation transcript
- The collected lead data
- Escalation status and reason

It returns a structured JSON with 8 fields covering intent, gaps, lead data, escalation info, and recommended next action. The `session_rating` field (`smooth | partial | escalated`) provides a quick quality signal for pipeline monitoring.

The summary is generated by a **separate system prompt** rather than the main FAQ prompt. This separation ensures the summary model is reasoning about the transcript as a whole, not continuing the customer conversation — a key architectural boundary.

---

## 8. Known Limitations

1. **No persistent memory across sessions** — each session starts fresh. A production system would load customer history from a CRM.
2. **No streaming** — responses are returned in full. For a real-time chat interface, streaming with `client.messages.stream()` would improve UX.
3. **Single-turn SOP** — the SOP is static per session. A production system would reload or hot-swap SOPs without restarting.
4. **Sentiment detection is model-dependent** — the escalation relies on Claude correctly identifying negative sentiment. For production, a dedicated lightweight sentiment classifier (e.g. fine-tuned DistilBERT) would add a parallel safety net.
5. **No auth or rate limiting** — appropriate for a prototype CLI but not for production deployment.