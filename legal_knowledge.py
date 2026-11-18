"""
legal_knowledge.py
------------------
Indian legal knowledge base: relevant Acts, Sections, consumer rights,
employment law, tenancy law, and common legal notice templates.

This module is intentionally factual and conservative — the AI cites only
well-established, publicly available legal provisions.
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class LegalProvision:
    act: str
    section: str
    description: str
    plain_english: str
    keywords: List[str] = field(default_factory=list)


@dataclass
class LegalCategory:
    name: str
    description: str
    provisions: List[LegalProvision]
    typical_forum: str          # Where to file: Consumer Court, Labour Court, etc.
    time_limit: Optional[str]   # Limitation period
    self_help_possible: bool    # Can person do it without a lawyer?


# ---------------------------------------------------------------------------
# Knowledge Base
# ---------------------------------------------------------------------------

LEGAL_KB: List[LegalCategory] = [

    # ── 1. Security Deposit / Tenancy ────────────────────────────────────────
    LegalCategory(
        name="security_deposit",
        description="Landlord not returning security deposit after vacating",
        typical_forum="Rent Control Authority / District Consumer Forum",
        time_limit="2 years from cause of action (Consumer Protection Act)",
        self_help_possible=True,
        provisions=[
            LegalProvision(
                act="Transfer of Property Act, 1882",
                section="Section 108(q)",
                description="Landlord must return deposit within reasonable time after tenancy ends.",
                plain_english="Your landlord is legally required to return your deposit once you've vacated and all dues are cleared.",
                keywords=["deposit", "security", "landlord", "refund", "rent"],
            ),
            LegalProvision(
                act="Consumer Protection Act, 2019",
                section="Section 2(7) & 35",
                description="Renting accommodation is a service; denial of deposit refund is a deficiency in service.",
                plain_english="You can file a consumer complaint if your landlord doesn't return the deposit — no lawyer needed.",
                keywords=["consumer", "complaint", "deficiency", "service"],
            ),
            LegalProvision(
                act="Indian Contract Act, 1872",
                section="Section 74",
                description="If a party breaches contract, the other can recover actual damages.",
                plain_english="If your landlord made illegal deductions from your deposit without proof of damage, you can sue for the full amount.",
                keywords=["contract", "breach", "damages", "deduction"],
            ),
        ],
    ),

    # ── 2. Unpaid Salary ─────────────────────────────────────────────────────
    LegalCategory(
        name="unpaid_salary",
        description="Employer hasn't paid salary",
        typical_forum="Labour Commissioner / Industrial Tribunal",
        time_limit="3 years under Payment of Wages Act; 1 year under ID Act",
        self_help_possible=True,
        provisions=[
            LegalProvision(
                act="Payment of Wages Act, 1936",
                section="Section 5",
                description="Wages must be paid by the 7th (or 10th) of the following month.",
                plain_english="Your employer must pay you by the 7th of next month. If they don't, you can file a complaint with the Labour Commissioner.",
                keywords=["salary", "wages", "unpaid", "employer", "delay"],
            ),
            LegalProvision(
                act="Payment of Wages Act, 1936",
                section="Section 15",
                description="Application to Labour Authority for recovery of unpaid wages.",
                plain_english="File a complaint with your area's Labour Commissioner — it's free and you don't need a lawyer.",
                keywords=["labour", "commissioner", "complaint", "recovery"],
            ),
            LegalProvision(
                act="Industrial Disputes Act, 1947",
                section="Section 33C",
                description="Recovery of money due from employer.",
                plain_english="If you're entitled to money the employer owes (arrears, overtime), the Labour Court can order recovery.",
                keywords=["industrial", "dispute", "arrears", "overtime"],
            ),
        ],
    ),

    # ── 3. Online / E-commerce Refund ────────────────────────────────────────
    LegalCategory(
        name="ecommerce_refund",
        description="Online purchase refund not received",
        typical_forum="Consumer Helpline / District Consumer Commission",
        time_limit="2 years from cause of action",
        self_help_possible=True,
        provisions=[
            LegalProvision(
                act="Consumer Protection Act, 2019",
                section="Section 2(7)(ii)",
                description="Online purchases are covered under the Act as 'service'.",
                plain_english="When you buy something online, you're a consumer — the law protects you.",
                keywords=["online", "ecommerce", "purchase", "refund", "amazon", "flipkart"],
            ),
            LegalProvision(
                act="Consumer Protection (E-Commerce) Rules, 2020",
                section="Rule 7(1)(e)",
                description="E-commerce sellers must have a clear return/refund policy and honour it.",
                plain_english="The seller is legally required to process refunds as per their own stated policy.",
                keywords=["refund", "policy", "ecommerce", "rules"],
            ),
            LegalProvision(
                act="Consumer Protection Act, 2019",
                section="Section 35",
                description="Consumer can file complaint without a lawyer before District Commission.",
                plain_english="You can file a consumer complaint yourself for free (up to ₹50 lakh) at your district consumer court.",
                keywords=["consumer court", "complaint", "district"],
            ),
        ],
    ),

    # ── 4. Legal Notice Reply ────────────────────────────────────────────────
    LegalCategory(
        name="legal_notice_reply",
        description="Received a legal notice and need to respond",
        typical_forum="Depends on notice type",
        time_limit="Typically 15–30 days from receipt of notice",
        self_help_possible=True,
        provisions=[
            LegalProvision(
                act="Code of Civil Procedure, 1908",
                section="Section 80",
                description="Before suing Government, 2-month notice required. Private parties may also send notice.",
                plain_english="A legal notice is NOT a court order — it's a formal letter. You have time to respond.",
                keywords=["legal notice", "reply", "response", "cpc"],
            ),
            LegalProvision(
                act="Limitation Act, 1963",
                section="Section 2(j)",
                description="Limitation periods — most civil suits must be filed within 3 years.",
                plain_english="Just because you received a notice doesn't mean you've lost. The other party still has to prove their claim in court.",
                keywords=["limitation", "time limit", "notice"],
            ),
        ],
    ),

    # ── 5. Consumer Complaint (General) ──────────────────────────────────────
    LegalCategory(
        name="consumer_complaint",
        description="Defective product or poor service",
        typical_forum="District Consumer Commission (up to ₹50 lakh)",
        time_limit="2 years from cause of action",
        self_help_possible=True,
        provisions=[
            LegalProvision(
                act="Consumer Protection Act, 2019",
                section="Section 2(9)",
                description="Consumer rights include right to be heard, right to redressal.",
                plain_english="You have the legal right to complain and get compensation for a bad product or service.",
                keywords=["defective", "product", "service", "complaint"],
            ),
            LegalProvision(
                act="Consumer Protection Act, 2019",
                section="Section 39",
                description="District Commission can award compensation, replacement, or refund.",
                plain_english="The consumer court can order the company to refund you, replace the product, or pay compensation.",
                keywords=["compensation", "replacement", "refund", "consumer court"],
            ),
        ],
    ),

    # ── 6. Money Recovery / Friendly Loan Dispute ─────────────────────────────
    LegalCategory(
        name="money_recovery",
        description="Friendly loan or personal money lent not returned",
        typical_forum="Civil Court (Summary Suit under Order 37 CPC) / Lok Adalat",
        time_limit="3 years from default date (Limitation Act, 1963)",
        self_help_possible=True,
        provisions=[
            LegalProvision(
                act="Indian Contract Act, 1872",
                section="Section 73",
                description="Compensation for loss or damage caused by breach of contract.",
                plain_english="Even informal or verbal agreements to repay money (supported by UPI/bank/chats) form a legally binding contract.",
                keywords=["money", "loan", "borrow", "borrowed", "lend", "debt", "giving back", "return back", "giving money", "given money", "repay", "repayment", "owe", "owes", "30000", "50000"],
            ),
            LegalProvision(
                act="Code of Civil Procedure, 1908",
                section="Order 37",
                description="Summary Suit for fast-track recovery of debts and liquidated demands.",
                plain_english="You can file an expedited summary suit in civil court to recover the debt without standard lengthy trials.",
                keywords=["summary suit", "order 37", "recovery", "cpc"],
            ),
            LegalProvision(
                act="Limitation Act, 1963",
                section="Article 19 & 21",
                description="Three-year limitation period to file a recovery suit from the date of loan or agreed repayment date.",
                plain_english="You have 3 years from the date they were supposed to return the money to initiate legal proceedings.",
                keywords=["limitation", "time limit", "3 years"],
            ),
        ],
    ),
]

# ---------------------------------------------------------------------------
# Helper: find best matching category
# ---------------------------------------------------------------------------

def find_legal_category(problem_text: str) -> Optional[LegalCategory]:
    """Return the best-matching LegalCategory for a problem description."""
    text_lower = problem_text.lower()
    best: Optional[LegalCategory] = None
    best_score = 0

    for cat in LEGAL_KB:
        score = 0
        for prov in cat.provisions:
            for kw in prov.keywords:
                if kw in text_lower:
                    score += 1
        if score > best_score:
            best_score = score
            best = cat

    return best if best_score > 0 else None


def get_relevant_provisions(problem_text: str) -> List[LegalProvision]:
    """Return all relevant legal provisions for a problem."""
    text_lower = problem_text.lower()
    results: List[LegalProvision] = []
    seen = set()

    for cat in LEGAL_KB:
        for prov in cat.provisions:
            for kw in prov.keywords:
                if kw in text_lower and prov.section not in seen:
                    results.append(prov)
                    seen.add(prov.section)
                    break

    return results


# ---------------------------------------------------------------------------
# Notice templates
# ---------------------------------------------------------------------------

LEGAL_NOTICE_TEMPLATE = """
{sender_city}, {date}

To,
{recipient_name}
{recipient_address}

**LEGAL NOTICE**

Subject: {subject}

Sir/Madam,

Under the instructions of my client, {client_name}, residing at {client_address},
I hereby serve upon you this legal notice as follows:

**FACTS:**
{facts}

**LEGAL BASIS:**
{legal_basis}

**DEMAND:**
{demand}

You are hereby called upon to comply with the above demand within **{deadline} days**
from the receipt of this notice, failing which my client shall be constrained to
initiate appropriate legal proceedings against you, at your risk and costs.

Kindly treat this as a **final notice** before legal action.

Yours faithfully,
{sender_name}
(On behalf of {client_name})
""".strip()

CONSUMER_COMPLAINT_TEMPLATE = """
Before the District Consumer Disputes Redressal Commission
{district}, {state}

**CONSUMER COMPLAINT NO. ___/20__**

Complainant: {complainant_name}
             {complainant_address}
             Phone: {complainant_phone}

Opposite Party: {op_name}
                {op_address}

**COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019**

**FACTS OF THE CASE:**
{facts}

**LEGAL GROUNDS:**
{legal_grounds}

**RELIEF SOUGHT:**
{relief}

**PRAYER:**
In view of the above, it is most humbly prayed that this Hon'ble Commission may
be pleased to:
1. Direct the Opposite Party to {main_relief};
2. Award compensation of ₹{compensation} for mental agony and harassment;
3. Award ₹{litigation_cost} towards litigation costs;
4. Pass such other order as this Commission deems fit.

Dated: {date}

Complainant
{complainant_name}
""".strip()
