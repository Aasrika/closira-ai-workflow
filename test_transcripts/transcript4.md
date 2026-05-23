# Test Transcript 4 — Lead Qualification
## Scenario: AI asks structured questions and produces a qualification summary

---

**Stage:** Lead Qualification (Stage 2)  
**Expected behaviour:** AI asks 3 structured questions one at a time, collects and stores responses  
**Result:** ✅ PASS

---

```
═══════════════════════════════════════════════════════════
  🌸  BLOOM AESTHETICS CLINIC — AI Support Assistant
═══════════════════════════════════════════════════════════

🌸 Bloom: Hello! Welcome to Bloom Aesthetics Clinic. I'm Bloom 🌸, your virtual assistant.
How can I help you today?

You: I'm thinking about getting Botox, how does it work?

🌸 Bloom: Great question! Botox (Anti-Wrinkle Injections) works by temporarily relaxing 
the muscles that cause expression lines. We treat areas including forehead lines, frown 
lines (the "11s" between your brows), and crow's feet around the eyes.

Sessions take about 30 minutes, and results typically last 3–4 months. Most clients 
describe the sensation as a mild pinch — and we can apply numbing cream if you'd prefer.

We always recommend starting with a free 20-minute consultation so our practitioner can 
assess your goals and recommend the best plan for you. 🌸

You: That sounds good, I'd like to book

🌸 Bloom: I'd be happy to help you book! Let me take a few quick details first.

──────────────────────────────────────────────────────────
📋  LEAD QUALIFICATION
──────────────────────────────────────────────────────────

🌸 Bloom: To help our team follow up with you, I have a couple of quick questions! 
First — which treatment are you most interested in: Botox, Fillers, Skin Boosters, 
or would you like to start with a Free Consultation?

You: Botox definitely, for my forehead mainly

🌸 Bloom: Perfect, thank you! And have you had any aesthetic treatments before, 
or would this be your first time?

You: First time, never had anything done

🌸 Bloom: That's great — our team is brilliant with first-timers and will make sure 
you feel completely comfortable. Last question: is there a particular day or time that 
tends to work best for you?

You: Weekday afternoons, preferably Tuesday or Wednesday

🌸 Bloom: Wonderful! Here's a quick summary of what I've got for you:

✅ Treatment interest: Botox (forehead focus)
✅ Experience level: First-time client
✅ Preferred time: Weekday afternoons — Tuesday or Wednesday

Our team will be in touch via WhatsApp to confirm a booking that works for you. 
We look forward to welcoming you to Bloom! 🌸

✅ Lead data collected:
{
  "treatment_interest": "Botox - forehead focus",
  "prior_experience": "First-time client",
  "preferred_time": "Weekday afternoons, Tuesday or Wednesday"
}
```

---

**Analysis:**
- AI asked all 3 qualification questions sequentially (not all at once)
- AI maintained warm, conversational tone throughout
- AI correctly summarised collected data before closing
- Lead data structured and stored correctly in JSON format
- No leading questions or assumptions about the customer's answers