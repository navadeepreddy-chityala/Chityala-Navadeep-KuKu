# Walkthrough Script
**Assignment:** Kuku — AI Generalist Assignment (Problem 2: Build an AI Lawyer)  
**Tool / App Demoed:** *Nyay (न्याय) — AI Legal Companion for India*  

---

### Introduction & Problem Framing
> *"Hi everyone, I'm presenting my solution for Problem 2: Build an AI Lawyer.*  
> *In India, millions of ordinary people face everyday legal issues—withheld rental deposits, unpaid wages in startups, or refused refunds from e-commerce sellers.*  
> *Most people give up because hiring a lawyer costs 20,000 to 50,000 rupees, which is more than the dispute itself. The law exists, but access is broken.*  
> *I built **Nyay**—a conversational AI designed specifically for Indian everyday law. It turns a messy story in Hindi or English into a clear legal case, generates ready-to-serve legal notices and consumer complaints, and even lets you practice arguing before you confront the other side."*

---

### Demo 1: Real-World Dispute (Landlord Withholding Deposit)
*(Action: Open `http://localhost:8000` or run `python demo.py`)*  
> *"Let's take a common case. A tenant in Bengaluru vacates their flat, and the landlord refuses to return a 70,000 rupee deposit, claiming 40,000 rupees for repainting and normal wear-and-tear.*  
> *Notice that the user can explain this naturally in Hinglish: 'Landlord deposit wapas nahi de raha hai.'*  
> *Here is what Nyay does:*  
> *1. It immediately diagnoses the legal domain—Tenancy under the Transfer of Property Act, 1882.*  
> *2. Crucially, **it does not hallucinate fake sections**. We grounded the legal citations into a deterministic statutory knowledge base. It cites Section 108(q) and clarifies that normal wear-and-tear cannot be deducted under settled law.*  
> *3. It generates a formal, formatted 15-Day Statutory Legal Notice ready to send via registered post, giving the landlord a deadline before court action."*

---

### Demo 2: Argument Practice (Roleplay Mode) & Boundary Testing
> *"Next is the practice feature. Most people feel intimidated confronting their landlord or employer. Nyay plays the role of the opposing party—arguing why the deduction is 'company policy'—and coaches the user on how to respond with statutory counter-arguments.*  
>  
> *Now, let's test safety and ethical boundaries.*  
> *What if a user asks for advice on a criminal case, like an illegal police extortion or bail?*  
> *(Action: Show Test Case 5 input)*  
> *Nyay immediately identifies this as a criminal and custodial matter. Rather than hallucinating dangerous criminal advice, it **safely declines** and provides immediate free legal aid contacts under Section 12 of the Legal Services Authorities Act, including the NALSA 15100 toll-free helpline."*

---

### Architecture, Scale & Swappability
> *"Under the hood:*  
> *• We gave the messy story parsing and conversational roleplay to the LLM.*  
> *• But we kept statutory citations, time-limits, and court petition templates strictly in code to eliminate hallucinations.*  
> *• At scale (hundreds of thousands of users), the classification and document drafting run locally for virtually zero cost, keeping the total blended cost per user under 30 paise.*  
> *• The model is completely decoupled in `ai_lawyer.py`—we can swap OpenAI with Gemini, Claude, or an open-source local model in just three lines of code for your technical interview."*

---

### Conclusion
> *"All 21 automated unit tests pass out of the box, and all 5 raw test outputs are included in the submission folder."*
