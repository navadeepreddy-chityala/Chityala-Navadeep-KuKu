"""
demo.py
-------
Interactive demo of the AI Lawyer.

This demo works in two modes:
1. MOCK mode  — No API key needed; uses hardcoded canned responses to show UX
2. LIVE mode  — Set OPENAI_API_KEY env variable for real AI responses

Run:
    python demo.py              # Interactive menu
    python demo.py --mock       # Force mock mode (no API key needed)
    python demo.py --document   # Document generation demo
"""

import sys
import os

# ─── Rich for pretty output ───────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich import print as rprint
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

from legal_knowledge import find_legal_category, get_relevant_provisions
from document_generator import generate_legal_notice, generate_consumer_complaint, generate_notice_reply


# ─── Helpers ──────────────────────────────────────────────────────────────────

def say(text: str, style: str = ""):
    if HAS_RICH:
        if style:
            console.print(text, style=style)
        else:
            console.print(Markdown(text))
    else:
        print(text)


def header(title: str):
    if HAS_RICH:
        console.print(Panel(f"[bold cyan]{title}[/bold cyan]", expand=False))
    else:
        print(f"\n{'='*60}\n  {title}\n{'='*60}")


def divider():
    if HAS_RICH:
        console.rule()
    else:
        print("-" * 60)


# ─── Mock responses (no API key needed) ──────────────────────────────────────

MOCK_RESPONSES = {
    "deposit": """
## I understand your situation 🏠

Your landlord is withholding your security deposit. This is unfortunately very common,
but **you have strong legal rights**.

**Here's where you stand:**
- Under the **Transfer of Property Act, 1882 (Section 108q)**, your landlord is legally
  obligated to return your deposit once you vacate and all dues are cleared.
- Under the **Consumer Protection Act, 2019**, you can file a consumer complaint —
  no lawyer required, and filing is free.

**Your options (in order of effort):**

1. 📧 **Send a formal legal notice** (easy, do it today)
   — A written demand via registered post gives the landlord 15 days to respond.
   — This often works without going to court.

2. 🏛️ **File a consumer complaint** at your District Consumer Commission
   — Free to file, no lawyer needed for amounts up to ₹50 lakh
   — Takes 3–6 months typically

3. ⚖️ **Small Claims Court / Civil Suit** (if above fail)

**What I need from you to draft your legal notice:**
- Your full name and address
- Landlord's name and address  
- Deposit amount and when you vacated
- Any written agreement?

> ⚠️ *I am an AI, not a licensed advocate. For important decisions, please consult a lawyer.*
""",
    "salary": """
## I hear you — this is wage theft, and it's illegal 💼

Your employer not paying your salary is a serious violation of **Indian labour law**.

**Key laws protecting you:**
- **Payment of Wages Act, 1936 (Section 5)**: Wages must be paid by the 7th of next month
- **Payment of Wages Act, 1936 (Section 15)**: You can file a complaint with the Labour Commissioner for free

**Your immediate next steps:**

1. 📝 **Document everything** — salary slips, appointment letter, bank statements showing non-payment
2. 📧 **Send a written demand** to HR/management (creates a paper trail)
3. 🏛️ **File a complaint with the Labour Commissioner** in your district
   — Free, no lawyer needed
   — They can order the employer to pay within 60 days

**How many months of salary are pending?** And do you have an appointment letter or salary slips?

> ⚠️ *I am an AI, not a licensed advocate. Please verify with a labour lawyer for complex cases.*
""",
    "default": """
## Hello! I'm Nyay, your AI legal assistant 🏛️

I can help you with everyday legal problems in India:

- 🏠 **Landlord not returning deposit**
- 💼 **Employer not paying salary**
- 📦 **Online refund not received**
- 📄 **Received a legal notice, need to reply**
- ⚖️ **Consumer complaint (defective product/service)**

**Tell me your problem in your own words** — in English or Hindi —
and I'll explain your rights and next steps.

> ⚠️ *I am an AI, not a licensed advocate. For complex legal matters, please consult a real lawyer.*
"""
}


def mock_chat(message: str) -> str:
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["deposit", "landlord", "rent", "security"]):
        return MOCK_RESPONSES["deposit"]
    elif any(w in msg_lower for w in ["salary", "wages", "employer", "payment"]):
        return MOCK_RESPONSES["salary"]
    else:
        return MOCK_RESPONSES["default"]


# ─── Document demo ────────────────────────────────────────────────────────────

def run_document_demo():
    header("📄 Document Generation Demo")

    say("\n### 1. Legal Notice — Security Deposit Recovery\n")
    cat = find_legal_category("landlord deposit")
    notice = generate_legal_notice(
        client_name="Priya Sharma",
        client_address="Flat 4B, Sunrise Apartments, Koramangala, Bengaluru 560034",
        client_city="Bengaluru",
        recipient_name="Mr. Mahesh Nair",
        recipient_address="12 HSR Layout, Sector 2, Bengaluru 560102",
        subject="Recovery of Security Deposit of ₹60,000",
        facts=(
            "I, Priya Sharma, resided at Flat 2A, 12 HSR Layout as a tenant under a rental "
            "agreement dated 01 March 2023. I vacated the said premises on 01 October 2024 "
            "after serving one month's notice as required. A security deposit of ₹60,000 was "
            "paid at the time of moving in. Despite vacating 6 weeks ago and multiple requests, "
            "the deposit has not been returned. No specific damage or outstanding dues have been "
            "communicated to justify any deduction."
        ),
        demand="Return the full security deposit of ₹60,000 within 15 days of receipt of this notice.",
        legal_category=cat,
        deadline_days=15,
    )
    say("```\n" + notice + "\n```")

    divider()

    say("\n### 2. Consumer Complaint — E-commerce Refund\n")
    complaint = generate_consumer_complaint(
        complainant_name="Amit Verma",
        complainant_address="23 Civil Lines, Allahabad 211001",
        complainant_phone="9876543210",
        district="Allahabad",
        state="Uttar Pradesh",
        op_name="Flipkart Internet Private Limited",
        op_address="Embassy Tech Village, Bengaluru 560103",
        facts=(
            "On 15 September 2024, the complainant purchased a smartphone (Model: XYZ Pro) "
            "for ₹25,000 from the Opposite Party's website. The product received was defective — "
            "the screen had dead pixels and the battery drained within 2 hours. A return request "
            "was raised within 48 hours but the Opposite Party refused, claiming the return window "
            "had expired. All correspondence is documented."
        ),
        main_relief="refund ₹25,000 for the defective smartphone",
        compensation=25000,
    )
    say("```\n" + complaint + "\n```")

    divider()

    say("\n### 3. Reply to Legal Notice\n")
    reply = generate_notice_reply(
        my_name="Rahul Singh",
        my_address="45 Sector 15, Noida 201301",
        my_city="Noida",
        sender_of_notice_name="ABC Pvt. Ltd.",
        sender_of_notice_address="10 Connaught Place, New Delhi",
        notice_date="01 November 2024",
        rebuttal=(
            "The allegations made in the notice are false, frivolous, and without merit. "
            "I have already paid all dues as evidenced by the attached bank receipts dated "
            "15 October 2024. The claimant has failed to acknowledge receipt of said payment."
        ),
        my_position=(
            "I have fully discharged all my obligations. No amount is outstanding. "
            "I reserve all my legal rights to seek damages for this harassment."
        ),
    )
    say("```\n" + reply + "\n```")


# ─── Interactive chat demo ────────────────────────────────────────────────────

def run_interactive_demo(use_mock: bool = False):
    header("⚖️  Nyay — AI Legal Assistant for India")
    say("> **Note:** This is an AI assistant, not a licensed advocate.")
    say("> For complex matters, please consult a real lawyer.\n")

    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if use_mock or not has_gemini:
        say("*Running in Grounded Offline Mode (Set GEMINI_API_KEY to connect live Google Gemini)*\n", style="yellow")
        chat_fn = mock_chat
    else:
        try:
            from ai_lawyer import AILawyer
            lawyer = AILawyer()
            chat_fn = lawyer.chat
            say("*Connected to Google Gemini — Live mode (gemini-1.5-flash)*\n", style="green")
        except Exception as e:
            say(f"*Could not load AILawyer: {e}. Falling back to mock.*\n", style="yellow")
            chat_fn = mock_chat

    # Initial greeting
    say(mock_chat("hello"))
    divider()

    while True:
        try:
            if HAS_RICH:
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
            else:
                user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "bye", "q"):
                say("\n*Goodbye! Good luck with your case. 🙏*")
                break

            response = chat_fn(user_input)
            divider()
            if HAS_RICH:
                console.print("[bold blue]Nyay:[/bold blue]")
                console.print(Markdown(response))
            else:
                print(f"\nNyay:\n{response}")
            divider()

        except KeyboardInterrupt:
            say("\n\n*Session ended. Goodbye!*")
            break


# ─── Menu ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--document" in args:
        run_document_demo()
    elif "--mock" in args:
        run_interactive_demo(use_mock=True)
    else:
        # Show menu
        header("⚖️  Nyay — AI Legal Assistant Demo")
        say("\nChoose a demo mode:\n")
        say("1. **Interactive Chat** (requires OPENAI_API_KEY or falls back to mock)")
        say("2. **Document Generation** (see sample legal notice, complaint, reply)")
        say("3. **Exit**\n")

        try:
            if HAS_RICH:
                choice = Prompt.ask("Choice", choices=["1", "2", "3"], default="1")
            else:
                choice = input("Choice [1/2/3]: ").strip() or "1"
        except KeyboardInterrupt:
            choice = "3"

        if choice == "1":
            run_interactive_demo()
        elif choice == "2":
            run_document_demo()
        else:
            say("*Goodbye!*")


if __name__ == "__main__":
    main()
