import json
import os
import sys
import datetime
from typing import Optional
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


MODEL = "llama-3.1-8b-instant"
SOP_FILE = "sop_data.json"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)



def load_sop(path: str) -> str:
    with open(path, "r") as f:
        sop = json.load(f)
    return json.dumps(sop, indent=2)

SOP_TEXT = load_sop(SOP_FILE)



FAQ_SYSTEM_PROMPT = f"""You are Bloom, a friendly and professional AI assistant for Bloom Aesthetics Clinic.

Your role is to answer customer enquiries using ONLY the information in the SOP document below.
You must NEVER invent, guess, or infer information that is not explicitly stated in the SOP.

## SOP DOCUMENT (your only source of truth):
{SOP_TEXT}

## Behaviour Rules:
1. Answer questions warmly and concisely using only the SOP above.
2. If a question cannot be answered from the SOP, respond with exactly this JSON flag:
   {{"escalate": true, "reason": "out_of_scope", "message": "<your polite message to the customer>"}}
3. If the customer expresses frustration, anger, or makes a complaint, respond with:
   {{"escalate": true, "reason": "sentiment_negative", "message": "<your empathetic message>"}}
4. If the customer asks to speak to a human or requests an agent, respond with:
   {{"escalate": true, "reason": "explicit_request", "message": "<your message>"}}
5. If the customer asks about pricing negotiation or discounts, respond with:
   {{"escalate": true, "reason": "pricing_negotiation", "message": "<your message>"}}
6. For medical questions beyond the listed side effects in the SOP, respond with:
   {{"escalate": true, "reason": "medical_question", "message": "<your message>"}}
7. For normal, answerable questions — respond naturally in plain text (NOT JSON).
8. Keep responses under 120 words. Be warm, clear, and professional.
9. Always sign off as "Bloom 🌸" on first contact.

## Tone:
Warm, reassuring, and professional. You are speaking to people interested in aesthetic treatments —
be sensitive, non-pushy, and never make medical claims beyond what the SOP states.
"""

QUALIFICATION_SYSTEM_PROMPT = """You are Bloom, a friendly AI assistant for Bloom Aesthetics Clinic.

You are now in the lead qualification stage. Your goal is to gather information about the customer
to help the clinic team follow up effectively.

Ask the following questions ONE AT A TIME (do not ask all at once):
1. "Which treatment are you most interested in — Botox, Fillers, Skin Boosters, or a Free Consultation?"
2. "Have you had any aesthetic treatments before, or would this be your first time?"
3. "Is there a particular date or time that works best for you to come in?"

After collecting all three answers:
- Summarise what you've gathered.
- Let them know the team will be in touch to confirm booking.
- Return a JSON object with this exact structure:
  {"qualification_complete": true, "data": {"treatment_interest": "...", "prior_experience": "...", "preferred_time": "..."}}

Rules:
- Be conversational, not robotic.
- If the customer goes off-topic, gently steer back.
- Never skip questions or assume answers.
"""

SUMMARY_SYSTEM_PROMPT = """You are an AI session summariser for Bloom Aesthetics Clinic.

Given a full conversation transcript, generate a structured JSON summary with these exact fields:
{
  "customer_intent": "...",
  "questions_asked": ["..."],
  "sop_gaps": ["..."],
  "lead_data": {
    "treatment_interest": "...",
    "prior_experience": "...",
    "preferred_time": "..."
  },
  "escalation_triggered": true/false,
  "escalation_reason": "..." or null,
  "recommended_next_action": "...",
  "session_rating": "smooth | partial | escalated"
}

Be factual. Only include information from the conversation. Use null for unknown fields.
"""



class ConversationState:
    def __init__(self):
        self.history: list[dict] = []           
        self.stage: str = "faq"                 
        self.lead_data: dict = {}               
        self.escalated: bool = False
        self.escalation_reason: Optional[str] = None
        self.unanswered_count: int = 0          
        self.session_log: list[dict] = []       

    def add_turn(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        self.session_log.append({
            "role": role,
            "content": content,
            "stage": self.stage,
            "timestamp": datetime.datetime.now().isoformat()
        })



client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def call_claude(system_prompt: str, messages: list[dict], max_tokens: int = 500) -> str:
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=full_messages
    )
    return response.choices[0].message.content.strip()



def handle_escalation(state: ConversationState, reason: str, message: str):
    state.escalated = True
    state.escalation_reason = reason
    state.stage = "escalated"

    reason_labels = {
        "out_of_scope": "Question outside SOP knowledge",
        "sentiment_negative": "Customer expressed frustration or complaint",
        "explicit_request": "Customer requested human agent",
        "pricing_negotiation": "Customer requested discount or price negotiation",
        "medical_question": "Medical question beyond SOP scope",
        "consecutive_unanswered": "3+ consecutive unanswered questions"
    }

    print(f"\n{'─'*60}")
    print(f"⚠️  ESCALATION TRIGGERED")
    print(f"   Reason: {reason_labels.get(reason, reason)}")
    print(f"{'─'*60}")
    print(f"\n🌸 Bloom: {message}")
    print(f"\n[A human agent has been notified. Session continuing for summary...]\n")

    # Log escalation event
    state.session_log.append({
        "role": "system",
        "content": f"ESCALATION: {reason}",
        "stage": "escalated",
        "timestamp": datetime.datetime.now().isoformat()
    })



def try_parse_json(text: str) -> Optional[dict]:
    """Attempt to extract and parse JSON from AI response."""
    try:
        
        return json.loads(text)
    except json.JSONDecodeError:
        pass
   
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return None



def handle_faq(state: ConversationState, user_input: str) -> bool:
    """
    Returns True if conversation should continue, False if escalated.
    """
    state.add_turn("user", user_input)

    response_text = call_claude(FAQ_SYSTEM_PROMPT, state.history)
    parsed = try_parse_json(response_text)

    if parsed and parsed.get("escalate"):
        reason = parsed.get("reason", "unknown")
        message = parsed.get("message", "Let me connect you with a human agent.")

        # Track consecutive unanswered questions
        if reason == "out_of_scope":
            state.unanswered_count += 1
            if state.unanswered_count >= 3:
                reason = "consecutive_unanswered"
        else:
            state.unanswered_count = 0

        state.add_turn("assistant", message)
        handle_escalation(state, reason, message)
        return False  # Stop FAQ stage
    else:
        state.unanswered_count = 0
        state.add_turn("assistant", response_text)
        print(f"\n🌸 Bloom: {response_text}\n")
        return True



def run_qualification(state: ConversationState):
    """Runs the 3-question qualification loop."""
    state.stage = "qualification"
    print(f"\n{'─'*60}")
    print("📋  LEAD QUALIFICATION")
    print(f"{'─'*60}\n")

  
    qual_history = [
        {"role": "user", "content": "Hi, I'd like to know more about your services."},
        {"role": "assistant", "content": "I'd love to help! To make sure I can assist you best, I have a few quick questions."}
    ]

    opening = call_claude(QUALIFICATION_SYSTEM_PROMPT, qual_history)
    print(f"🌸 Bloom: {opening}\n")
    state.add_turn("assistant", opening)
    qual_history.append({"role": "assistant", "content": opening})

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        state.add_turn("user", user_input)
        qual_history.append({"role": "user", "content": user_input})

        response_text = call_claude(QUALIFICATION_SYSTEM_PROMPT, qual_history, max_tokens=600)
        parsed = try_parse_json(response_text)

        if parsed and parsed.get("qualification_complete"):
            state.lead_data = parsed.get("data", {})
            # Extract the conversational message (before the JSON)
            text_part = response_text[:response_text.find("{")].strip()
            if text_part:
                print(f"\n🌸 Bloom: {text_part}\n")
                state.add_turn("assistant", text_part)
            print(f"\n✅ Lead data collected: {json.dumps(state.lead_data, indent=2)}\n")
            break
        else:
            qual_history.append({"role": "assistant", "content": response_text})
            state.add_turn("assistant", response_text)
            print(f"\n🌸 Bloom: {response_text}\n")



def generate_summary(state: ConversationState) -> dict:
    """Generates a structured end-of-session summary."""
    state.stage = "summary"

    # Build transcript for summariser
    transcript_lines = []
    for entry in state.session_log:
        if entry["role"] in ("user", "assistant"):
            label = "Customer" if entry["role"] == "user" else "Bloom (AI)"
            transcript_lines.append(f"{label}: {entry['content']}")

    transcript = "\n".join(transcript_lines)

    summary_prompt = f"""Here is the full conversation transcript:

{transcript}

Lead data collected during qualification:
{json.dumps(state.lead_data, indent=2)}

Escalation occurred: {state.escalated}
Escalation reason: {state.escalation_reason}

Generate the structured JSON summary now."""

    summary_messages = [{"role": "user", "content": summary_prompt}]
    raw_summary = call_claude(SUMMARY_SYSTEM_PROMPT, summary_messages, max_tokens=800)

    parsed = try_parse_json(raw_summary)
    if not parsed:
        parsed = {"raw_summary": raw_summary, "parse_error": True}

    return parsed



def save_session(state: ConversationState, summary: dict):
    """Saves full session log and summary to the logs/ directory."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{LOG_DIR}/session_{timestamp}.json"

    output = {
        "session_id": timestamp,
        "escalated": state.escalated,
        "escalation_reason": state.escalation_reason,
        "lead_data": state.lead_data,
        "summary": summary,
        "full_log": state.session_log
    }

    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Session saved to: {filename}")



def run_conversation():
    print("\n" + "═"*60)
    print("  🌸  BLOOM AESTHETICS CLINIC — AI Support Assistant")
    print("  Powered by Closira | Type 'exit' to end session")
    print("═"*60 + "\n")

    state = ConversationState()

    welcome = (
        "Hello! Welcome to Bloom Aesthetics Clinic. I'm Bloom 🌸, your virtual assistant.\n"
        "I can help with questions about our treatments, pricing, and booking.\n"
        "How can I help you today?"
    )
    print(f"🌸 Bloom: {welcome}\n")
    state.add_turn("assistant", welcome)

   
    faq_turn_count = 0
    qualify_triggered = False

    while not state.escalated:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
            print(f"\n🌸 Bloom: Thank you for reaching out to Bloom Aesthetics! We hope to see you soon. 🌸\n")
            break

        # Check if user wants to book / qualify (triggers stage 2)
        booking_keywords = ["book", "appointment", "schedule", "come in", "visit", "available", "slot"]
        if any(kw in user_input.lower() for kw in booking_keywords) and faq_turn_count >= 1:
            qualify_triggered = True
            print(f"\n🌸 Bloom: I'd be happy to help you book! Let me take a few quick details first.\n")
            break

        faq_turn_count += 1
        should_continue = handle_faq(state, user_input)

        if not should_continue:
            # Escalated — skip to summary
            break

        # After 3 FAQ turns, offer qualification
        if faq_turn_count == 3 and not state.escalated:
            print(f"\n🌸 Bloom: You seem like you might be interested in booking with us! "
                  f"Would you like me to take a few details so our team can follow up?\n")
            follow_up = input("You: ").strip().lower()
            state.add_turn("user", follow_up)
            if any(w in follow_up for w in ["yes", "sure", "ok", "please", "yeah", "yep"]):
                qualify_triggered = True
                break

    
    if qualify_triggered and not state.escalated:
        run_qualification(state)

   
    print(f"\n{'─'*60}")
    print("📊  GENERATING SESSION SUMMARY...")
    print(f"{'─'*60}\n")

    summary = generate_summary(state)

    print("SESSION SUMMARY:")
    print(json.dumps(summary, indent=2))

    save_session(state, summary)

    print("\n" + "═"*60)
    print("  Session ended. Thank you for using Closira.")
    print("═"*60 + "\n")



if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
      print("❌ Error: GROQ_API_KEY environment variable not set.")
      print("   Run: export GROQ_API_KEY=your_key_here")
      sys.exit(1)

    run_conversation()