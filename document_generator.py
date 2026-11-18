"""
document_generator.py
----------------------
Generates legal documents (notices, complaints, replies) from structured data.
No AI required — pure template filling with smart defaults.
"""

from datetime import date, timedelta
from legal_knowledge import (
    LEGAL_NOTICE_TEMPLATE,
    CONSUMER_COMPLAINT_TEMPLATE,
    LegalCategory,
    get_relevant_provisions,
)


def _today() -> str:
    return date.today().strftime("%d %B %Y")


def _indian_number(n: int) -> str:
    """Format an integer in Indian numbering system (e.g. 1,00,000)."""
    s = str(n)
    if len(s) <= 3:
        return s
    # Last 3 digits, then groups of 2
    result = s[-3:]
    s = s[:-3]
    while s:
        result = s[-2:] + "," + result
        s = s[:-2]
    return result


def _deadline_date(days: int = 15) -> str:
    return (date.today() + timedelta(days=days)).strftime("%d %B %Y")


# ---------------------------------------------------------------------------
# Legal Notice
# ---------------------------------------------------------------------------

def generate_legal_notice(
    client_name: str,
    client_address: str,
    client_city: str,
    recipient_name: str,
    recipient_address: str,
    subject: str,
    facts: str,
    demand: str,
    legal_category: LegalCategory,
    deadline_days: int = 15,
) -> str:
    """Generate a formatted legal notice."""

    provisions = legal_category.provisions
    legal_basis_lines = [
        f"- {p.act}, {p.section}: {p.description}"
        for p in provisions[:3]  # top 3 provisions
    ]
    legal_basis = "\n".join(legal_basis_lines)

    return LEGAL_NOTICE_TEMPLATE.format(
        sender_city=client_city,
        date=_today(),
        recipient_name=recipient_name,
        recipient_address=recipient_address,
        subject=subject,
        client_name=client_name,
        client_address=client_address,
        facts=facts,
        legal_basis=legal_basis,
        demand=demand,
        deadline=deadline_days,
        sender_name=client_name,
    )


# ---------------------------------------------------------------------------
# Consumer Complaint
# ---------------------------------------------------------------------------

def generate_consumer_complaint(
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
    litigation_cost: int = 10000,
) -> str:
    """Generate a consumer complaint draft."""

    provisions = get_relevant_provisions(facts)
    legal_grounds_lines = [
        f"{i+1}. {p.act}, {p.section}: {p.plain_english}"
        for i, p in enumerate(provisions[:4])
    ]
    legal_grounds = "\n".join(legal_grounds_lines) if legal_grounds_lines else (
        "1. Consumer Protection Act, 2019 — deficiency in service / unfair trade practice."
    )

    relief = (
        f"- Refund / compensation as per the facts above\n"
        f"- ₹{_indian_number(compensation)} compensation for mental agony\n"
        f"- ₹{_indian_number(litigation_cost)} litigation cost"
    )

    return CONSUMER_COMPLAINT_TEMPLATE.format(
        district=district,
        state=state,
        complainant_name=complainant_name,
        complainant_address=complainant_address,
        complainant_phone=complainant_phone,
        op_name=op_name,
        op_address=op_address,
        facts=facts,
        legal_grounds=legal_grounds,
        relief=relief,
        main_relief=main_relief,
        compensation=_indian_number(compensation),
        litigation_cost=_indian_number(litigation_cost),
        date=_today(),
    )


# ---------------------------------------------------------------------------
# Reply to Legal Notice
# ---------------------------------------------------------------------------

NOTICE_REPLY_TEMPLATE = """
{sender_city}, {date}

To,
{sender_of_notice_name}
{sender_of_notice_address}

**RE: YOUR LEGAL NOTICE DATED {notice_date}**

Sir/Madam,

I, {my_name}, residing at {my_address}, have received your legal notice
dated {notice_date}. I respond as follows:

**RESPONSE TO YOUR ALLEGATIONS:**
{rebuttal}

**MY POSITION:**
{my_position}

**WITHOUT PREJUDICE:**
I deny all allegations made in your notice and reserve all my legal rights.
Your notice is based on incorrect facts and is misconceived. I am not liable
for the amounts / actions alleged therein.

Yours faithfully,
{my_name}
Dated: {date}
""".strip()


def generate_notice_reply(
    my_name: str,
    my_address: str,
    my_city: str,
    sender_of_notice_name: str,
    sender_of_notice_address: str,
    notice_date: str,
    rebuttal: str,
    my_position: str,
) -> str:
    """Generate a reply to a received legal notice."""
    return NOTICE_REPLY_TEMPLATE.format(
        sender_city=my_city,
        date=_today(),
        sender_of_notice_name=sender_of_notice_name,
        sender_of_notice_address=sender_of_notice_address,
        notice_date=notice_date,
        my_name=my_name,
        my_address=my_address,
        rebuttal=rebuttal,
        my_position=my_position,
    )
