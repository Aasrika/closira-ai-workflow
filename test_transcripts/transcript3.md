# Test Transcript 3 — Escalation Trigger
## Scenario: Customer expresses frustration / complaint

---

**Stage:** FAQ  
**Expected behaviour:** AI detects sentiment and escalates with reason logged  
**Result:** ✅ PASS

---

```
═══════════════════════════════════════════════════════════
  🌸  BLOOM AESTHETICS CLINIC — AI Support Assistant
═══════════════════════════════════════════════════════════

🌸 Bloom: Hello! Welcome to Bloom Aesthetics Clinic. I'm Bloom 🌸, your virtual assistant.
How can I help you today?

You: I had fillers done last week and my face is still really swollen and uneven. 
     I'm not happy at all and I want to know what you're going to do about this.

──────────────────────────────────────────────────────────
⚠️  ESCALATION TRIGGERED
   Reason: Customer expressed frustration or complaint
──────────────────────────────────────────────────────────

🌸 Bloom: I'm so sorry to hear you're experiencing this — that must be really worrying, 
and I completely understand your concern. This isn't something I should handle over chat. 
I'm flagging this to our clinic team right now so someone can call you back as soon as 
possible to make this right. Please don't hesitate to reach us directly on WhatsApp at 
+44 7700 900123. 🌸

[A human agent has been notified. Session continuing for summary...]

SESSION SUMMARY:
{
  "customer_intent": "Complaint about post-filler swelling and asymmetry after recent treatment",
  "questions_asked": ["Complaint about post-treatment results"],
  "sop_gaps": ["No aftercare or complaint resolution process documented in SOP"],
  "lead_data": {},
  "escalation_triggered": true,
  "escalation_reason": "sentiment_negative",
  "recommended_next_action": "Urgent callback from practitioner. Review treatment records. Consider documenting complaint handling process in SOP.",
  "session_rating": "escalated"
}
```

---

**Analysis:**
- AI correctly detected frustrated/complaint sentiment ("not happy at all")
- AI did NOT attempt to medically diagnose or explain the swelling
- AI escalated immediately with an empathetic, reassuring message
- AI provided the WhatsApp contact (from SOP) as a direct escalation channel
- Escalation reason logged as `sentiment_negative`
- Summary correctly identifies SOP gap: no complaint handling procedure documented