# Kuku AI Generalist Assignment — Solution Document
**Candidate Submission for Problem 2: Build an AI Lawyer**  
**Project Name:** *Nyay (न्याय) — Everyday Legal Companion for India*  
**Repository / Working Directory:** `C:\Users\nav9n\Downloads\Kuku\ai_lawyer`  
**Prototype Interface:** Local Web UI (`http://localhost:8000`) & Interactive Terminal CLI (`ai_lawyer.py`)  
**Core Model Engine:** Google Gemini (`gemini-flash-latest`) + Grounded Offline Indian Statutory KB  

---

## 1. Problem Choice & Executive Framing

### Why Problem 2?
Every year in India, tens of millions of ordinary citizens forfeit rightful funds—withheld rental deposits (₹40,000–₹1,00,000), 2–3 months of unpaid salary in unorganized startups, refused refunds for defective goods, or unpaid personal loans. A private advocate typically demands an upfront retainer of ₹15,000 to ₹50,000, making legal recourse mathematically irrational for disputes below ₹2,00,000. People give up not because the law is against them, but because the **transaction cost and complexity of the legal system exceed the claim**.

*Nyay* solves this by functioning as an accessible, bilingual legal companion: extracting facts from conversational narrative, grounding legal standing in verified Indian statutes, generating ready-to-serve formal documents, and roleplaying opponent pushbacks.

### Scope & Legal Domains
Rather than attempting to hallucinate across all ~1,200 Indian acts, *Nyay* deliberately focuses with **rigorous depth on the everyday 80%**:
1. **Tenancy Disputes:** Security deposit withholding, arbitrary repair/painting deductions (*Transfer of Property Act, 1882*, Sec 108(q)).
2. **Wage Theft & Employment:** Unpaid salary arrears, delayed wages (*Payment of Wages Act, 1936*, Sec 5 & 15).
3. **E-Commerce Grievances:** Defective merchandise, refusal to refund (*Consumer Protection Act, 2019*, *E-Commerce Rules, 2020*).
4. **Friendly Loan & Money Recovery:** Personal debts, loans without stamp paper (*Indian Contract Act, 1872*, Sec 73; *Code of Civil Procedure, 1908*, Order 37 Summary Suits; *Limitation Act, 1963*).
5. **Notice Period Rebuttals:** Responding to employer or commercial threatening notices without panic (*Code of Civil Procedure, 1908*).
6. **Consumer Deficiencies:** Defective services and misleading trade practices (*Consumer Protection Act, 2019*, Sec 35 & 39).

### Crucial Assumptions & Core Principles
- **Colloquial Vernacular / Hinglish:** Users communicate in informal Hinglish (e.g., *"Maine pichle saal 30000 diye the wapas nahi de raha"*). The system parses intent without demanding formal legal phrasing.
- **Zero Hallucination Policy:** Hallucinated section numbers or phantom citations cause legal damage. All statutory citations are strictly anchored to a verified knowledge base (`legal_knowledge.py`).
- **Tangible Actionability:** The user needs concrete next actions—a formal 15-day statutory legal notice, consumer complaint draft, or negotiation counter-strategy.
- **Strict Safety Boundaries:** Criminal proceedings, police extortion, arrest threats, and domestic violence are safely declined with immediate referrals to DLSA and the **NALSA National Legal Aid Helpline (15100)**.

---

## 2. Approach: What We Gave to AI vs. What We Kept in Deterministic Code

| Component | Technical Implementation | Architectural Rationale |
| :--- | :--- | :--- |
| **User Narrative Understanding & Dialogue** | **Google Gemini (`gemini-flash-latest`)** | Parses messy, emotionally stressed vernacular accounts; handles multi-turn clarification questions in English, Hindi, and Hinglish. |
| **Statutory Knowledge & Section Grounding** | **Deterministic KB (`legal_knowledge.py`)** | **Completely prevents AI hallucinations.** Verified acts, sections, time limits, and forums are retrieved deterministically. |
| **Document Drafting Engine** | **Algorithmic Template Engine (`document_generator.py`)** | Procedural legal documents (Legal Notices, Section 35 Complaints, Rebuttals) follow strict court-tested formatting with Indian number system formatting (e.g., ₹1,00,000). |
| **Practice / Argument Drill** | **LLM Opponent Simulation** | Rehearses the opponent’s expected stance (landlord, employer, debtor) and equips the user with evidence-backed counter-arguments. |
| **Out-of-Scope Safety Gate** | **Deterministic Keyword & Safety Filter** | Intercepts criminal matters immediately before token generation to prevent accidental legal harm or liability. |
| **Offline Resilience** | **Zero-Dependency Grounded Engine** | If the internet disconnects or API limits are hit, the system gracefully falls back to deterministic statutory advice without crashing. |

---

## 3. End-to-End System Architecture

```
[User Input (Text/Hinglish/English)]
                  │
                  ▼
 ┌────────────────────────────────────────────────────────┐
 │ Step 0: Safety Boundary Guard                          │──► [Criminal/Police: Safe Refusal &
 │ (Detects FIR, Police, Arrest, Custodial threats)       │     Immediate DLSA / NALSA 15100 Referral]
 └────────────────────────────────────────────────────────┘
                  │ (Civil / Consumer / Contractual)
                  ▼
 ┌────────────────────────────────────────────────────────┐
 │ Step 1: Case Diagnosis & Fact Extraction               │
 │ (Extracts amounts, dates, relationship, agreements)   │
 └────────────────────────────────────────────────────────┘
                  │
                  ▼
 ┌────────────────────────────────────────────────────────┐
 │ Step 2: Statutory Anchoring (Deterministic KB)         │
 │ (Transfer of Property Act, Contract Act, CPC, CPA 2019)│
 └────────────────────────────────────────────────────────┘
                  │
                  ▼
 ┌────────────────────────────────────────────────────────┐
 │ Step 3: Plain-Language AI Legal Counsel (Gemini)       │
 │ (Empathetic breakdown, rights explanation, roadmap)    │
 └────────────────────────────────────────────────────────┘
                  │
                  ▼
 ┌────────────────────────────────────────────────────────┐
 │ Step 4: Ready-to-Serve Document Generation             │
 │ (15-Day Statutory Legal Notice / Consumer Complaint)   │
 └────────────────────────────────────────────────────────┘
                  │
                  ▼
 ┌────────────────────────────────────────────────────────┐
 │ Step 5: "Argument Drill" (Simulating Opponent Pushback)│
 └────────────────────────────────────────────────────────┘
```

---

## 4. Scale, Unit Economics & Cost Efficiency

At consumer scale (500,000 active disputes per month across Tier 1, 2, and 3 India):
- **Hybrid Cost Structure:**
  - Category diagnosis, statute grounding, and safety checks run locally at **₹0.00 compute cost**.
  - Vernacular synthesis runs on Google Gemini (Flash tier).
  - Total token consumption: ~1,200 tokens per full dispute analysis.
  - **Estimated cost per complete legal resolution + drafted notice: ~₹0.15 to ₹0.30 ($0.002 to $0.004)**.
- **Zero-Dependency Portability:**
  - The entire stack runs on **standard Python 3.10+ (zero pip packages required)**. Built-in `urllib.request` and `http.server` ensure zero operational overhead.
- **Human-In-The-Loop (HITL) Tiering:**
  - *Tier 1 (Automated):* Disputes under ₹2,00,000 resolved through automated notices and consumer court self-filings.
  - *Tier 2 (Escalation):* Complex matters with corporate cross-notices are handed off to empanelled legal aid or junior advocates.

---

## 5. Evaluation, Quality Assurance & Test Cases

We evaluated the system across **6 benchmark scenarios** representing real Indian disputes (full unedited JSON and Markdown outputs are preserved in `raw_outputs/`):

1. **TC-01 (Tenant Deposit Withholding - Bengaluru):** Disallows repainting deductions without damage invoices under *Transfer of Property Act Sec 108(q)*; drafts 15-day formal notice.
2. **TC-02 (Unpaid Startup Wages - Noida):** Enforces *Payment of Wages Act Sec 5 & 15*; counters the employer’s "investor funding delay" excuse.
3. **TC-03 (E-Commerce Defective Laptop - Punjab):** Rejects the platform's "intermediary shield" under *Consumer Protection (E-Commerce) Rules 2020*; generates Section 35 Consumer Complaint.
4. **TC-04 (Notice Period Buyout Rebuttal - Hyderabad):** Formulates a structured *Without Prejudice* legal reply adjusting notice shortfall against earned leaves.
5. **TC-05 (Police Intimidation & Safety Boundary Test):** Safely refuses advice on criminal extortion; immediately routes user to DLSA and NALSA Helpline 15100.
6. **TC-06 (Personal Loan & Debt Recovery Dispute):** Validates informal loan agreements under *Indian Contract Act Sec 73*, explains the 3-year limitation under the *Limitation Act 1963*, and drafts an *Order 37 CPC* summary demand notice.

### Automated Test Suite:
- **28 Automated Tests** in `test_cases.py` covering knowledge retrieval, legal categorization, boundary safety enforcement, and template formatting. All pass cleanly.

### Honest Limitations & Edge Cases:
- **Mandatory Arbitration Clauses:** When corporate employment contracts contain mandatory arbitration clauses under the *Arbitration and Conciliation Act, 1996*, consumer commissions may lack jurisdiction.
- **Purely Cash Disputes Without Digital Audit Trails:** If a loan was given in physical cash without bank/UPI transfers or WhatsApp logs, evidence under Section 65B of the Indian Evidence Act is difficult to establish.
- **Limitation Period Expiry:** Claims beyond 3 years are time-barred under the *Limitation Act, 1963*; the system actively warns users to avoid fruitless litigation.

---

## 6. How to Run the Prototype

The prototype is 100% functional, self-contained, and ready to evaluate immediately:

```bash
# 1. Run the Web Application (Interactive UI on localhost:8000)
python web_app.py
# Open http://localhost:8000 in any browser

# 2. Run the Interactive Terminal AI Lawyer
python ai_lawyer.py

# 3. Run the CLI Demo Walkthrough
python demo.py

# 4. Run the Automated Test Suite (28 Tests)
python test_cases.py

# 5. Regenerate Benchmark Raw Outputs (6 Scenarios)
python generate_raw_outputs.py
```

### Self-Contained Deliverables Included:
- **Web App Prototype (`web_app.py`):** Interactive browser application with one-click test presets, live Gemini dialogue, document previewer, and practice drill cards.
- **Terminal Prototype (`ai_lawyer.py`):** Interactive command-line legal assistant.
- **6 Benchmark Raw Outputs (`raw_outputs/`):** Full, unedited model outputs (.json and .md) for all evaluation scenarios.
- **Solution Document (`SOLUTION_DOCUMENT.md` & `SOLUTION_DOCUMENT.html`):** Complete design and architecture breakdown.
