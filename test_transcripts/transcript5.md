# Test Transcript 5 — Conversation Summary
## Scenario: Full session with mixed FAQ + qualification, ending with structured summary

---

**Stage:** All stages  
**Expected behaviour:** AI produces a clean, structured summary with intent, details, and next action  
**Result:** ✅ PASS

---

```
═══════════════════════════════════════════════════════════
  🌸  BLOOM AESTHETICS CLINIC — AI Support Assistant
═══════════════════════════════════════════════════════════

🌸 Bloom: Hello! Welcome to Bloom Aesthetics Clinic. I'm Bloom 🌸, your virtual assistant.
How can I help you today?

You: Hi, what's the difference between Botox and fillers?

🌸 Bloom: Great question! Here's a quick comparison:

**Botox** relaxes the muscles that cause expression lines (like forehead wrinkles and 
crow's feet). Results last 3–4 months, starting from £200.

**Dermal Fillers** add volume and definition to areas like lips, cheeks, and jawline — 
they don't relax muscles but literally fill and sculpt. Results last 6–18 months depending 
on the area, starting from £250.

Both treatments are done by our qualified practitioners and take under an hour. 
A free consultation is the best way to figure out which — or which combination — is right 
for you! 🌸

You: Can I get both done on the same day?

🌸 Bloom: Yes! Combination treatments are absolutely possible. Our practitioners will 
discuss the best approach during your free 20-minute consultation, where they'll assess 
your goals and recommend the right plan. Would you like to explore booking one? 🌸

You: How much would a full face treatment cost?

──────────────────────────────────────────────────────────
⚠️  ESCALATION TRIGGERED
   Reason: Question outside SOP knowledge
──────────────────────────────────────────────────────────

🌸 Bloom: Ooh, that's a great question but one that really needs a personalised quote! 
Full-face treatment costs vary based on exactly which areas are treated and the products 
used — it's not something I can quote accurately here. I'll flag this for one of our 
specialists to get back to you with a tailored estimate. 🌸

[A human agent has been notified. Session continuing for summary...]

──────────────────────────────────────────────────────────
📊  GENERATING SESSION SUMMARY...
──────────────────────────────────────────────────────────

SESSION SUMMARY:
{
  "customer_intent": "Researching the difference between Botox and fillers, interested in combination full-face treatment with pricing",
  "questions_asked": [
    "What is the difference between Botox and fillers?",
    "Can I get both done on the same day?",
    "How much would a full face treatment cost?"
  ],
  "sop_gaps": [
    "Full-face combination treatment pricing not specified in SOP",
    "No bundled package pricing documented"
  ],
  "lead_data": {},
  "escalation_triggered": true,
  "escalation_reason": "out_of_scope",
  "recommended_next_action": "Human specialist to contact customer with personalised full-face treatment quote. Consider adding combination package pricing to SOP.",
  "session_rating": "partial"
}

💾 Session saved to: logs/session_20250601_143022.json
```

---

**Analysis:**
- AI correctly answered both in-SOP questions (Botox vs fillers, combination treatments)
- AI correctly escalated on the out-of-scope full-face pricing question rather than guessing
- Summary correctly captured all 3 questions asked
- SOP gaps correctly identified (no bundle/package pricing in SOP)
- Recommended next action is actionable and specific
- `session_rating` correctly set to `partial` (some answered, one escalated)