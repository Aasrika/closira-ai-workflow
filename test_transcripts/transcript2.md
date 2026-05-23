# Test Transcript 2 — Out-of-Scope Question
## Scenario: Customer asks something not in the SOP

---

**Stage:** FAQ  
**Expected behaviour:** AI acknowledges the gap and escalates rather than guessing  
**Result:** ✅ PASS

---

```
═══════════════════════════════════════════════════════════
  🌸  BLOOM AESTHETICS CLINIC — AI Support Assistant
═══════════════════════════════════════════════════════════

🌸 Bloom: Hello! Welcome to Bloom Aesthetics Clinic. I'm Bloom 🌸, your virtual assistant.
How can I help you today?

You: Do you offer laser hair removal?

──────────────────────────────────────────────────────────
⚠️  ESCALATION TRIGGERED
   Reason: Question outside SOP knowledge
──────────────────────────────────────────────────────────

🌸 Bloom: That's a great question! Laser hair removal isn't a service I have details about 
right now, and I'd rather connect you with someone who can give you the right answer than 
guess. Let me pass you over to one of our team members who can help. 🌸

[A human agent has been notified. Session continuing for summary...]

SESSION SUMMARY:
{
  "customer_intent": "Enquiring about laser hair removal services",
  "questions_asked": ["Do you offer laser hair removal?"],
  "sop_gaps": ["Laser hair removal not listed in SOP services"],
  "lead_data": {},
  "escalation_triggered": true,
  "escalation_reason": "out_of_scope",
  "recommended_next_action": "Human agent to confirm whether laser hair removal is offered and provide pricing if applicable. Consider adding service to SOP.",
  "session_rating": "escalated"
}
```

---

**Analysis:**
- AI correctly identified the question was outside its SOP
- AI did NOT guess or invent a response about laser hair removal
- AI escalated with a warm, non-dismissive message
- Escalation reason logged correctly as `out_of_scope`
- Summary correctly identifies an SOP gap and recommends updating the SOP