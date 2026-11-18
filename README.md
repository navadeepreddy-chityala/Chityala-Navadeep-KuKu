# Nyay (न्याय) — AI Legal Companion for India
**Kuku AI Generalist Assignment — Problem 2: Build an AI Lawyer**

An AI-powered legal assistant designed to help ordinary citizens in India navigate everyday legal problems in their own language (English, Hindi, or Hinglish), understand their statutory rights, draft formal legal documents, and practice negotiation without high legal fees.

Powered by **Google Gemini** (`gemini-flash-latest`) with a **deterministic Indian statutory knowledge base** and zero-dependency architecture.

---

## 🌟 Key Capabilities

1. **Natural Colloquial & Hinglish Dialogue:**
   - Understands everyday narratives (e.g., *"Maine pichle saal 30000 diye the wapas nahi de raha"*, *"Landlord deposit nahi de raha"*).
   - Asks structured clarifying diagnostic questions (amounts, transfer mode, written proof, timeline).

2. **Zero-Hallucination Statutory Grounding:**
   - All citations are grounded in verified Indian statutes (`legal_knowledge.py`):
     - *Transfer of Property Act, 1882* (Sec 108(q) – Tenancy & Security Deposits)
     - *Payment of Wages Act, 1936* (Sec 5 & 15 – Unpaid Salary & Wage Arrears)
     - *Consumer Protection Act, 2019* (Sec 35 & 39 – Defective Goods & Services)
     - *Consumer Protection (E-Commerce) Rules, 2020* (Rule 7 – Online Refund Denials)
     - *Indian Contract Act, 1872* (Sec 73 – Friendly Loans & Debt Recovery)
     - *Code of Civil Procedure, 1908* (Order 37 – Fast-track Summary Debt Suits)
     - *Limitation Act, 1963* (3-year statutory windows)

3. **Automated Document Drafting:**
   - Instantly generates ready-to-serve procedural drafts:
     - **15-Day Statutory Legal Demand Notice** (Tenancy, Unpaid Salary, Debt Recovery)
     - **Section 35 Consumer Complaint Petition** (E-Commerce, Defective Goods)
     - **Formal "Without Prejudice" Notice Rebuttal** (Notice Period Buyout Demands)
   - Adheres to Indian number formatting (e.g., ₹1,00,000).

4. **Interactive Opponent Roleplay Drill:**
   - Simulates the opposing party's most likely counter-argument (e.g., landlord claiming painting deductions, employer claiming startup cashflow issues, borrower claiming lack of stamp paper).
   - Provides concrete legal rebuttal tips citing statutory precedents and Section 65B of the Indian Evidence Act.

5. **Strict Safety Boundary & Free Legal Aid Routing:**
   - Intercepts criminal matters, police extortion, custody disputes, and arrest threats.
   - Refuses advice safely and connects the user to **District Legal Services Authority (DLSA)** and the **National Legal Services Authority (NALSA) Helpline (15100)** for free legal aid under Section 12 of the Legal Services Authorities Act, 1987.

---

## 📁 Project Structure

```
ai_lawyer/
├── web_app.py               # Local Web UI with live Gemini dialogue & document preview
├── ai_lawyer.py             # Core conversational AI engine (Gemini + offline fallback)
├── gemini_client.py         # Zero-dependency Google Gemini REST client (built-in urllib)
├── legal_knowledge.py       # Grounded Indian statutory database & templates
├── document_generator.py    # Algorithmic legal notice & complaint drafting engine
├── demo.py                  # Guided CLI walkthrough
├── test_cases.py            # Automated test suite (28 test cases)
├── generate_raw_outputs.py  # Benchmark runner for 6 realistic test scenarios
├── raw_outputs/             # Unedited raw outputs (.json & .md) for all test cases
├── SOLUTION_DOCUMENT.md     # Official 2-Page Solution Document
├── SOLUTION_DOCUMENT.html   # Print-ready formatted version for PDF export
├── requirements.txt         # Optional dependencies (Standard library only required)
├── .env                     # API key configuration
└── .env.example             # Configuration template
```

---

## 🚀 Quick Start (Zero External Packages Required!)

The entire system runs on Python 3.10+ standard library. No `pip install` required!

### 1. Launch the Web Application (Recommended)
```bash
python web_app.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.
- Interactive chat in English, Hindi, or Hinglish.
- Left sidebar with 6 one-click test scenarios covering tenancy, wage theft, e-commerce, debt recovery, notice reply, and criminal safety boundary.
- Live document generator preview and practice rebuttal drills.

### 2. Interactive Terminal AI Lawyer
```bash
python ai_lawyer.py
```
- Direct conversational interface in your command line.
- Grounded responses powered by Google Gemini.

### 3. Run Automated Tests
```bash
python test_cases.py
```
- Runs 28 unit and integration tests verifying categorization, statutory citations, safety bounds, and document formatting.

### 4. Inspect or Regenerate Benchmark Outputs
```bash
python generate_raw_outputs.py
```
- Generates unedited JSON and Markdown outputs for all 6 test cases in the `raw_outputs/` folder.

---

## 🔑 Google Gemini Configuration

The system uses `gemini-flash-latest` with automatic fallback chain.
The API key is loaded automatically from `.env`:
```
GEMINI_API_KEY=your_key_here
```
Or set via environment variable:
- **PowerShell:** `$env:GEMINI_API_KEY="your_key"`
- **CMD:** `set GEMINI_API_KEY=your_key`
- **Linux/macOS:** `export GEMINI_API_KEY="your_key"`

*Note: If no internet or API key is provided, the system seamlessly falls back to its deterministic offline statutory engine.*

---

## 📄 Submission Documents

- **Solution Document:** [SOLUTION_DOCUMENT.md](file:///C:/Users/nav9n/Downloads/Kuku/ai_lawyer/SOLUTION_DOCUMENT.md) / [SOLUTION_DOCUMENT.html](file:///C:/Users/nav9n/Downloads/Kuku/ai_lawyer/SOLUTION_DOCUMENT.html)
- **Raw Benchmark Outputs:** Located in [`raw_outputs/`](file:///C:/Users/nav9n/Downloads/Kuku/ai_lawyer/raw_outputs/)
- **Self-Contained Evaluation:** Everything is runnable locally with reproducible test cases, verifiable outputs, and an intuitive web UI.
