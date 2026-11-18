"""
ai_lawyer.py
------------
Core AI Lawyer — a conversational AI that helps ordinary people in India
navigate everyday legal problems.

Design principles
-----------------
1. HONEST   — Never invents case law; cites only real provisions from legal_knowledge.py
2. HUMBLE   — Explicitly says when it can't help and refers to a real lawyer
3. ACTIONABLE — Gives step-by-step next actions, not just information
4. PLAIN    — Uses simple language the user is comfortable with
5. SAFE     — Never provides advice in life-threatening or criminal matters
"""

import os
import json
from typing import Optional

from gemini_client import GeminiClient, DEFAULT_MODEL as DEFAULT_GEMINI_MODEL

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    OPENAI_AVAILABLE = False

from legal_knowledge import (
    find_legal_category,
    get_relevant_provisions,
    LegalCategory,
)
from document_generator import (
    generate_legal_notice,
    generate_consumer_complaint,
    generate_notice_reply,
)

# ---------------------------------------------------------------------------
# System prompt — the "soul" of the AI Lawyer
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are "Nyay" (meaning Justice in Hindi), an AI legal assistant
designed to help ordinary people in India understand and act on everyday legal problems.

## WHO YOU ARE
You are NOT a licensed advocate. You are a knowledgeable helper who:
- Explains legal situations in simple, plain language (Hindi or English)
- Identifies which laws apply and what options exist
- Helps prepare legal documents like notices and complaints
- Practices arguments with the user (roleplaying as the other side)
- Knows your limits and refers users to real lawyers when needed

## RULES YOU ALWAYS FOLLOW
1. NEVER invent case citations or fake legal sections — only use what you know to be real.
2. If a question involves criminal law, violence, or life safety, immediately say:
   "This is beyond what I can help with. Please contact the police or a lawyer immediately."
3. Always remind the user: "I am an AI, not a licensed advocate. For important decisions,
   please consult a real lawyer."
4. Use simple, conversational language. Avoid jargon unless you explain it.
5. Ask clarifying questions before giving advice — understand the full situation.
6. After explaining options, always give a clear NEXT STEP.
7. If the user writes in Hindi/Hinglish, respond in Hinglish.

## CONVERSATION FLOW
Step 1: UNDERSTAND — Ask questions to understand the full situation (who, what, when, how much)
Step 2: DIAGNOSE — Identify the legal category (tenancy, employment, consumer, etc.)
Step 3: EXPLAIN — Tell them where they stand in plain language
Step 4: OPTIONS — List their options (self-help, complaint, notice, mediation, court)
Step 5: ACTION — Help them take the next step (draft a document, explain the process)
Step 6: PRACTICE (optional) — Roleplay as the other side so they can practice

## WHAT YOU CAN HELP WITH
- Security deposit disputes with landlord
- Unpaid salary / wage theft
- E-commerce refund issues
- Consumer complaints (defective products/services)
- Understanding and replying to legal notices
- Drafting basic legal notices and consumer complaints

## WHAT TO REFER OUT
- Criminal matters (FIR, arrest, bail)
- Property ownership disputes
- Family law (divorce, custody, inheritance) — complex, refer to lawyer
- Corporate/business law
- Tax disputes

## TONE
Warm, calm, and supportive. Many users are stressed and scared.
Begin by acknowledging their situation before diving into law.
"""

# ---------------------------------------------------------------------------
# Classifier prompt — categorize the problem
# ---------------------------------------------------------------------------

CLASSIFY_PROMPT = """Given this user problem description, return a JSON object with:
{
  "category": one of ["security_deposit", "unpaid_salary", "ecommerce_refund", 
                       "legal_notice_reply", "consumer_complaint", "criminal", 
                       "family_law", "unknown"],
  "confidence": "high" | "medium" | "low",
  "summary": "one sentence summary of the core problem",
  "urgency": "urgent" | "normal",
  "needs_real_lawyer": true | false,
  "reason_if_referral": "why they need a real lawyer, or null"
}

User problem: {problem}

Return ONLY the JSON, no explanation."""

# ---------------------------------------------------------------------------
# AI Lawyer class
# ---------------------------------------------------------------------------

class AILawyer:
    """
    Conversational AI legal assistant for India.

    Usage
    -----
    lawyer = AILawyer()
    response = lawyer.chat("My landlord is not returning my deposit of ₹50,000")
    print(response)
    """

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_GEMINI_MODEL):
        self.model = model
        self.gemini_client = GeminiClient(api_key=api_key, model=model)
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.current_category: Optional[LegalCategory] = None
        self.classified = False

    # ── Public API ────────────────────────────────────────────────────────────

    def chat(self, user_message: str) -> str:
        """Send a message and get a response."""
        # Check criminal/safety boundary first
        criminal_words = ["police", "fir", "arrest", "jail", "bail", "criminal", "extortion"]
        if any(w in user_message.lower() for w in criminal_words):
            refusal = (
                "⚠️ **CRITICAL DISCLAIMER & REFERRAL**\n\n"
                "This situation involves criminal law or police action. As an AI assistant, "
                "I am strictly programmed **NOT** to provide guidance on criminal or custodial matters "
                "to prevent serious legal harm.\n\n"
                "**Immediate Action Steps:**\n"
                "1. Consult an enrolled criminal advocate immediately.\n"
                "2. If you cannot afford counsel, you are entitled to free legal aid under Section 12 "
                "of the Legal Services Authorities Act, 1987 via your local District Legal Services Authority (DLSA).\n"
                "3. NALSA National Toll-Free Legal Aid Helpline: **15100**."
            )
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": refusal})
            return refusal

        # First message: auto-classify and enrich context
        if not self.classified:
            self._classify_and_enrich(user_message)
            self.classified = True

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # If Google Gemini is configured, use it
        if self.gemini_client.is_configured:
            try:
                assistant_message = self.gemini_client.generate(
                    contents=self.conversation_history,
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3,
                    max_output_tokens=1500,
                )
            except Exception as e:
                # If network or API key error, fall back gracefully
                print(f"[Warning] Gemini API call failed: {e}. Falling back to grounded offline engine.")
                assistant_message = self._offline_chat_response(user_message)
        else:
            # Deterministic, grounded offline intelligence engine
            assistant_message = self._offline_chat_response(user_message)

        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        return assistant_message

    def _offline_chat_response(self, user_message: str) -> str:
        """Fallback response grounded in the verified Indian legal knowledge base."""
        if not self.current_category:
            return (
                "Namaste! I am Nyay, your legal assistant.\n\n"
                "I can help you understand and act on everyday Indian legal problems, including:\n"
                "- Landlord withholding security deposits\n"
                "- Employer delaying or refusing salary\n"
                "- E-commerce seller refusing refunds for damaged goods\n"
                "- Responding to threatening legal notices\n\n"
                "Please describe what happened, who is involved, and what amount is in dispute."
            )

        provisions = get_relevant_provisions(user_message)
        prov_lines = [f"• **{p.act} ({p.section})**: {p.plain_english}" for p in provisions]
        prov_text = "\n".join(prov_lines) if prov_lines else "• Consumer Protection Act / Contract Act general protections apply."

        return (
            f"### ⚖️ Legal Assessment: {self.current_category.name.replace('_', ' ').title()}\n\n"
            f"**Your Legal Standing:**\n"
            f"Under Indian law, you have a valid, actionable dispute. You do not necessarily need an expensive private lawyer for this.\n\n"
            f"**Key Statutory Provisions (Verified Grounding):**\n"
            f"{prov_text}\n\n"
            f"**Procedural Roadmap:**\n"
            f"1. **Forum:** {self.current_category.typical_forum}\n"
            f"2. **Limitation Period:** {self.current_category.time_limit}\n"
            f"3. **Self-Representation:** {'Allowed without an advocate' if self.current_category.self_help_possible else 'Advocate representation advised'}\n\n"
            f"**Next Concrete Action:**\n"
            f"I can draft a formal **15-Day Statutory Legal Notice** or a **Consumer Complaint** for you. "
            f"Simply provide: your name & address, opposing party's name & address, and exact dates/amounts.\n\n"
            f"> *Note: Running in grounded offline mode (zero API cost). To connect live Google Gemini, set GEMINI_API_KEY.*"
        )

    def draft_legal_notice(
        self,
        client_name: str,
        client_address: str,
        client_city: str,
        recipient_name: str,
        recipient_address: str,
        subject: str,
        facts: str,
        demand: str,
        deadline_days: int = 15,
    ) -> str:
        """Generate a legal notice based on current conversation context."""
        if not self.current_category:
            return "❌ Please describe your problem first so I can identify the right legal framework."

        return generate_legal_notice(
            client_name=client_name,
            client_address=client_address,
            client_city=client_city,
            recipient_name=recipient_name,
            recipient_address=recipient_address,
            subject=subject,
            facts=facts,
            demand=demand,
            legal_category=self.current_category,
            deadline_days=deadline_days,
        )

    def draft_consumer_complaint(
        self,
        complainant_name: str,
        complainant_address: str,
        complainant_phone: str,
        district: str,
        state: str,
        op_name: str,
        op_address: str,
        facts: str,
        main_relief: str,
        compensation: int = 50000,
    ) -> str:
        """Generate a consumer complaint."""
        return generate_consumer_complaint(
            complainant_name=complainant_name,
            complainant_address=complainant_address,
            complainant_phone=complainant_phone,
            district=district,
            state=state,
            op_name=op_name,
            op_address=op_address,
            facts=facts,
            main_relief=main_relief,
            compensation=compensation,
        )

    def draft_notice_reply(
        self,
        my_name: str,
        my_address: str,
        my_city: str,
        sender_name: str,
        sender_address: str,
        notice_date: str,
        rebuttal: str,
        my_position: str,
    ) -> str:
        """Generate a reply to a legal notice."""
        return generate_notice_reply(
            my_name=my_name,
            my_address=my_address,
            my_city=my_city,
            sender_of_notice_name=sender_name,
            sender_of_notice_address=sender_address,
            notice_date=notice_date,
            rebuttal=rebuttal,
            my_position=my_position,
        )

    def roleplay_other_side(self, user_position: str) -> str:
        """Practice mode: AI plays the other side to help user prepare."""
        if self.gemini_client.is_configured:
            roleplay_prompt = f"""
The user wants to practice their case. 
Their position: {user_position}
Their current legal category: {self.current_category.name if self.current_category else "unknown"}

Play the role of the opposing party (landlord / employer / company).
Make reasonable counter-arguments they might actually face.
After your counter-argument, give the user a TIP on how to respond.
Keep it conversational and constructive.
"""
            try:
                return self.gemini_client.generate(
                    contents=[{"role": "user", "content": roleplay_prompt}],
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.5,
                    max_output_tokens=800,
                )
            except Exception as e:
                print(f"[Warning] Gemini roleplay failed: {e}. Using offline drill.")

        cat_name = self.current_category.name if self.current_category else "general"
        if cat_name == "security_deposit":
            return (
                "🥊 **Opposing Landlord Persona:**\n"
                "\"Look, you vacated the flat with deep stains and the walls needed a total repaint. "
                "The contract says the property must be returned in original condition. That ₹40,000 "
                "barely covered my painting contractor bills!\"\n\n"
                "💡 **Strategy Tip for Your Rebuttal:**\n"
                "Remind them that settled Indian tenancy law distinguishes between willful damage and "
                "routine wear-and-tear. Demand actual GST invoices of the painting expenses. If they cannot "
                "produce itemized bills dated immediately after your handover, their deduction is legally untenable."
            )
        elif cat_name == "unpaid_salary":
            return (
                "🥊 **Opposing Employer Persona:**\n"
                "\"The startup has been struggling with venture capital disbursement delays. We asked everyone "
                "to be patient. You leaving abruptly causes business disruption!\"\n\n"
                "💡 **Strategy Tip for Your Rebuttal:**\n"
                "State firmly that under Section 5 of the Payment of Wages Act, payment of earned wages by the 7th/10th "
                "of each month is a mandatory statutory liability. Company cashflow risk cannot be passed on to employees."
            )
        else:
            return (
                "🥊 **Opposing Party Persona:**\n"
                "\"Our terms of service clearly state that transactions once completed are non-refundable.\"\n\n"
                "💡 **Strategy Tip for Your Rebuttal:**\n"
                "Remind them that unilateral terms of service cannot contract out of the Consumer Protection Act, 2019 "
                "regarding deficiency in service or unfair trade practices."
            )

    def reset(self):
        """Start a new conversation."""
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.current_category = None
        self.classified = False

    # ── Private helpers ───────────────────────────────────────────────────────

    def _classify_and_enrich(self, problem_text: str) -> None:
        """Classify the problem and inject legal context into the system prompt."""
        # Rule-based classification (no API call needed)
        category = find_legal_category(problem_text)
        provisions = get_relevant_provisions(problem_text)

        if category:
            self.current_category = category
            context = self._build_legal_context(category, provisions)
            # Inject as a system message so the LLM has the right context
            self.conversation_history.append({
                "role": "system",
                "content": f"[LEGAL CONTEXT DETECTED]\n{context}"
            })

    def _build_legal_context(self, category: LegalCategory, provisions) -> str:
        lines = [
            f"Category: {category.name}",
            f"Typical forum: {category.typical_forum}",
            f"Time limit: {category.time_limit or 'check with lawyer'}",
            f"Can do without lawyer: {'Yes' if category.self_help_possible else 'Lawyer recommended'}",
            "",
            "Relevant legal provisions:",
        ]
        for p in provisions:
            lines.append(f"  • {p.act}, {p.section}: {p.plain_english}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI Interactive Loop
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("  ⚖️  Nyay — AI Legal Assistant for India (Google Gemini)")
    print("=" * 65)

    lawyer = AILawyer()

    # If no key is configured or key was invalid, offer one-time setup
    if not lawyer.gemini_client.is_configured:
        print("\n[Optional AI Setup]")
        print("To enable Google Gemini, paste your API key below (starts with 'AIzaSy...').")
        print("Get a free key at: https://aistudio.google.com/")
        print("Or press [Enter] to continue in Free Grounded Offline Mode.")
        try:
            user_key = input("\nPaste Gemini API Key (or press Enter to skip): ").strip()
            if user_key:
                lawyer.gemini_client.set_key(user_key, save_to_env=True)
                print("✓ Gemini API Key configured successfully!\n")
            else:
                print("✓ Continuing in Free Grounded Mode (Zero API cost).\n")
        except (KeyboardInterrupt, EOFError):
            print()

    if lawyer.gemini_client.is_configured:
        print("🤖 Mode: Connected to Google Gemini (gemini-1.5-flash)")
    else:
        print("🏛️ Mode: Grounded Statutory Engine (Deterministic & Free)")

    print("-" * 65)
    print("Type your legal problem in plain English or Hinglish (e.g. 'Landlord deposit nahi de raha').")
    print("Type 'exit' or 'quit' to end session.\n")

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("\nSession ended. Good luck with your matter!")
                break
            response = lawyer.chat(user_input)
            print(f"\nNyay:\n{response}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nSession closed.")
            break
