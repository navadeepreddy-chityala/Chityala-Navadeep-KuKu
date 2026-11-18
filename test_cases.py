"""
test_cases.py
-------------
Unit and integration tests for the AI Lawyer system.

Tests are grouped into:
1. Legal knowledge base tests (pure logic, no API)
2. Document generator tests (pure logic, no API)
3. AI Lawyer classification tests (no API)
4. Integration tests (require OPENAI_API_KEY — skipped if not set)

Run:  python test_cases.py
      python test_cases.py -v        # verbose
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import date

# ── Imports ──────────────────────────────────────────────────────────────────
from legal_knowledge import (
    find_legal_category,
    get_relevant_provisions,
    LEGAL_KB,
    LegalCategory,
)
from document_generator import (
    generate_legal_notice,
    generate_consumer_complaint,
    generate_notice_reply,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Legal Knowledge Base Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestLegalKnowledgeBase(unittest.TestCase):

    def test_kb_has_expected_categories(self):
        """Knowledge base contains all required categories."""
        names = {cat.name for cat in LEGAL_KB}
        required = {
            "security_deposit",
            "unpaid_salary",
            "ecommerce_refund",
            "legal_notice_reply",
            "consumer_complaint",
        }
        self.assertTrue(required.issubset(names), f"Missing: {required - names}")

    def test_all_categories_have_provisions(self):
        """Every category has at least one legal provision."""
        for cat in LEGAL_KB:
            self.assertGreater(
                len(cat.provisions), 0,
                f"Category '{cat.name}' has no provisions"
            )

    def test_all_provisions_have_required_fields(self):
        """Every provision has act, section, description, and plain_english."""
        for cat in LEGAL_KB:
            for prov in cat.provisions:
                self.assertTrue(prov.act, f"Missing act in {cat.name}")
                self.assertTrue(prov.section, f"Missing section in {cat.name}")
                self.assertTrue(prov.description, f"Missing description in {cat.name}")
                self.assertTrue(prov.plain_english, f"Missing plain_english in {cat.name}")

    def test_find_category_security_deposit(self):
        """Deposit-related text matches security_deposit category."""
        problem = "My landlord is not returning my security deposit of ₹50,000"
        cat = find_legal_category(problem)
        self.assertIsNotNone(cat)
        self.assertEqual(cat.name, "security_deposit")

    def test_find_category_unpaid_salary(self):
        """Salary-related text matches unpaid_salary category."""
        problem = "My employer hasn't paid my salary for 3 months"
        cat = find_legal_category(problem)
        self.assertIsNotNone(cat)
        self.assertEqual(cat.name, "unpaid_salary")

    def test_find_category_ecommerce(self):
        """Online purchase refund text matches ecommerce_refund category."""
        problem = "I ordered something online and the refund never came. Amazon is not responding"
        cat = find_legal_category(problem)
        self.assertIsNotNone(cat)
        self.assertEqual(cat.name, "ecommerce_refund")

    def test_find_category_legal_notice(self):
        """Legal notice text matches legal_notice_reply category."""
        problem = "I received a legal notice from my previous employer"
        cat = find_legal_category(problem)
        self.assertIsNotNone(cat)
        self.assertEqual(cat.name, "legal_notice_reply")

    def test_find_category_consumer_complaint(self):
        """Defective product matches consumer_complaint."""
        problem = "I bought a defective refrigerator and the company refuses to replace it"
        cat = find_legal_category(problem)
        self.assertIsNotNone(cat)
        self.assertEqual(cat.name, "consumer_complaint")

    def test_find_category_unknown_returns_none_or_low_score(self):
        """Unrelated text returns None (or at least doesn't crash)."""
        result = find_legal_category("How is the weather today?")
        # Should return None since no keywords match
        self.assertIsNone(result)

    def test_get_relevant_provisions_deposit(self):
        """Returns provisions for deposit problem."""
        provisions = get_relevant_provisions("landlord not returning deposit")
        self.assertGreater(len(provisions), 0)

    def test_get_relevant_provisions_no_duplicates(self):
        """Provisions list has no duplicate sections."""
        provisions = get_relevant_provisions("landlord deposit salary wages")
        sections = [p.section for p in provisions]
        self.assertEqual(len(sections), len(set(sections)))

    def test_self_help_possible_flags(self):
        """Check that consumer-facing categories are marked self_help_possible."""
        for cat in LEGAL_KB:
            if cat.name in ("security_deposit", "ecommerce_refund", "consumer_complaint"):
                self.assertTrue(
                    cat.self_help_possible,
                    f"Category '{cat.name}' should be self-help possible"
                )

    def test_time_limits_present(self):
        """Most categories should have time limits specified."""
        cats_with_limits = [c for c in LEGAL_KB if c.time_limit]
        self.assertGreater(len(cats_with_limits), 3)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Document Generator Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestDocumentGenerator(unittest.TestCase):

    def setUp(self):
        """Common test data."""
        self.deposit_category = find_legal_category("landlord deposit")
        self.today = date.today().strftime("%d %B %Y")

    # ── Legal Notice ──────────────────────────────────────────────────────────

    def test_legal_notice_contains_parties(self):
        """Legal notice includes sender and recipient names."""
        notice = generate_legal_notice(
            client_name="Rahul Sharma",
            client_address="12 MG Road, Bengaluru",
            client_city="Bengaluru",
            recipient_name="Suresh Landlord",
            recipient_address="45 HSR Layout, Bengaluru",
            subject="Recovery of Security Deposit",
            facts="I vacated the property on 1 Oct 2024. Deposit of ₹50,000 not returned.",
            demand="Return ₹50,000 within 15 days.",
            legal_category=self.deposit_category,
        )
        self.assertIn("Rahul Sharma", notice)
        self.assertIn("Suresh Landlord", notice)

    def test_legal_notice_contains_legal_basis(self):
        """Legal notice cites relevant acts."""
        notice = generate_legal_notice(
            client_name="Priya Patel",
            client_address="Test Address",
            client_city="Mumbai",
            recipient_name="Mr. Landlord",
            recipient_address="Test",
            subject="Security Deposit",
            facts="Deposit not returned.",
            demand="Return deposit.",
            legal_category=self.deposit_category,
        )
        # Should cite at least one known Act
        self.assertTrue(
            any(act in notice for act in [
                "Transfer of Property Act",
                "Consumer Protection Act",
                "Indian Contract Act"
            ]),
            "Notice should cite relevant legislation"
        )

    def test_legal_notice_contains_today_date(self):
        """Legal notice has today's date."""
        notice = generate_legal_notice(
            client_name="Test User",
            client_address="Test",
            client_city="Delhi",
            recipient_name="Test Recipient",
            recipient_address="Test",
            subject="Test",
            facts="Test facts.",
            demand="Test demand.",
            legal_category=self.deposit_category,
        )
        self.assertIn(self.today, notice)

    def test_legal_notice_has_legal_notice_header(self):
        """Legal notice has LEGAL NOTICE header."""
        notice = generate_legal_notice(
            client_name="X", client_address="Y", client_city="Z",
            recipient_name="A", recipient_address="B",
            subject="S", facts="F", demand="D",
            legal_category=self.deposit_category,
        )
        self.assertIn("LEGAL NOTICE", notice)

    def test_legal_notice_custom_deadline(self):
        """Custom deadline days appear in notice."""
        notice = generate_legal_notice(
            client_name="X", client_address="Y", client_city="Z",
            recipient_name="A", recipient_address="B",
            subject="S", facts="F", demand="D",
            legal_category=self.deposit_category,
            deadline_days=30,
        )
        self.assertIn("30", notice)

    # ── Consumer Complaint ────────────────────────────────────────────────────

    def test_consumer_complaint_has_required_sections(self):
        """Consumer complaint has complainant, OP, and prayer sections."""
        complaint = generate_consumer_complaint(
            complainant_name="Amit Kumar",
            complainant_address="10 Civil Lines, Allahabad",
            complainant_phone="9876543210",
            district="Allahabad",
            state="Uttar Pradesh",
            op_name="Flipkart Internet Pvt. Ltd.",
            op_address="Bangalore",
            facts="Ordered phone, received broken unit, refund denied.",
            main_relief="refund ₹25,000 for defective product",
            compensation=25000,
        )
        self.assertIn("Amit Kumar", complaint)
        self.assertIn("Flipkart", complaint)
        self.assertIn("PRAYER", complaint)
        self.assertIn("Consumer Protection Act", complaint)

    def test_consumer_complaint_compensation_formatting(self):
        """Compensation amount is formatted in Indian number system."""
        complaint = generate_consumer_complaint(
            complainant_name="X",
            complainant_address="Y",
            complainant_phone="1234567890",
            district="Delhi",
            state="Delhi",
            op_name="Z Corp",
            op_address="Z",
            facts="Bad service.",
            main_relief="refund",
            compensation=100000,
        )
        # Indian format: 1,00,000 not 100,000
        self.assertIn("1,00,000", complaint)

    # ── Notice Reply ──────────────────────────────────────────────────────────

    def test_notice_reply_has_re_header(self):
        """Notice reply references the original notice date."""
        reply = generate_notice_reply(
            my_name="Ravi Singh",
            my_address="23 Sector 15, Noida",
            my_city="Noida",
            sender_of_notice_name="ABC Company",
            sender_of_notice_address="Delhi",
            notice_date="01 November 2024",
            rebuttal="The allegations are baseless.",
            my_position="I have already paid all dues.",
        )
        self.assertIn("01 November 2024", reply)
        self.assertIn("Ravi Singh", reply)
        self.assertIn("WITHOUT PREJUDICE", reply)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. AI Lawyer Classification Tests (no API call)
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from ai_lawyer import AILawyer as _AILawyerCls
    _OPENAI_IMPORTABLE = True
except ImportError:
    _OPENAI_IMPORTABLE = False


@unittest.skipUnless(_OPENAI_IMPORTABLE, "Skipping: 'openai' package not installed")

@unittest.skipUnless(_OPENAI_IMPORTABLE, "Skipping: 'openai' package not installed")
class TestAILawyerClassification(unittest.TestCase):
    """
    Test the AILawyer._classify_and_enrich logic without making API calls.
    We mock the OpenAI client.
    """

    def _make_mock_lawyer(self):
        """Create AILawyer with a mocked OpenAI client."""
        with patch("ai_lawyer.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client

            # Mock the chat completion response
            mock_response = MagicMock()
            mock_response.choices[0].message.content = "I understand your problem. Let me help."
            mock_client.chat.completions.create.return_value = mock_response

            from ai_lawyer import AILawyer
            lawyer = AILawyer(api_key="test-key")
            lawyer.client = mock_client
            return lawyer, mock_client

    def test_classify_deposit_problem(self):
        """Deposit problem is classified into security_deposit category."""
        lawyer, _ = self._make_mock_lawyer()
        lawyer._classify_and_enrich("My landlord won't return my deposit of ₹30,000")
        self.assertIsNotNone(lawyer.current_category)
        self.assertEqual(lawyer.current_category.name, "security_deposit")

    def test_classify_salary_problem(self):
        """Salary problem is classified into unpaid_salary category."""
        lawyer, _ = self._make_mock_lawyer()
        lawyer._classify_and_enrich("My employer hasn't paid my salary for 2 months")
        self.assertIsNotNone(lawyer.current_category)
        self.assertEqual(lawyer.current_category.name, "unpaid_salary")

    def test_classify_ecommerce_problem(self):
        """E-commerce problem is classified correctly."""
        lawyer, _ = self._make_mock_lawyer()
        lawyer._classify_and_enrich("Ordered online, refund not received from Amazon")
        self.assertIsNotNone(lawyer.current_category)
        self.assertEqual(lawyer.current_category.name, "ecommerce_refund")

    def test_legal_context_injected_into_history(self):
        """After classification, legal context is added to conversation history."""
        lawyer, _ = self._make_mock_lawyer()
        initial_len = len(lawyer.conversation_history)
        lawyer._classify_and_enrich("landlord won't return deposit")
        # Should have added a system message with legal context
        self.assertGreater(len(lawyer.conversation_history), initial_len)
        # Last injected message should be from system role
        injected = [m for m in lawyer.conversation_history if m["role"] == "system"]
        self.assertGreater(len(injected), 1)  # original + injected context

    def test_reset_clears_state(self):
        """Reset clears conversation history and category."""
        lawyer, _ = self._make_mock_lawyer()
        lawyer._classify_and_enrich("deposit problem")
        lawyer.reset()
        self.assertIsNone(lawyer.current_category)
        self.assertFalse(lawyer.classified)
        self.assertEqual(len(lawyer.conversation_history), 1)  # just system prompt

    def test_draft_notice_without_classification_returns_error(self):
        """draft_legal_notice fails gracefully if no category detected."""
        lawyer, _ = self._make_mock_lawyer()
        result = lawyer.draft_legal_notice(
            client_name="X", client_address="Y", client_city="Z",
            recipient_name="A", recipient_address="B",
            subject="S", facts="F", demand="D",
        )
        self.assertIn("❌", result)

    def test_chat_adds_to_history(self):
        """chat() adds user and assistant messages to history."""
        lawyer, mock_client = self._make_mock_lawyer()
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Here is my advice."
        mock_client.chat.completions.create.return_value = mock_response

        # Set classified so we don't trigger classification branch
        lawyer.classified = True
        lawyer.chat("My landlord isn't returning my deposit")
        # History: system + user + assistant
        roles = [m["role"] for m in lawyer.conversation_history]
        self.assertIn("user", roles)
        self.assertIn("assistant", roles)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Integration Tests (require real OPENAI_API_KEY)
# ═══════════════════════════════════════════════════════════════════════════════

@unittest.skipUnless(
    os.getenv("OPENAI_API_KEY"),
    "Skipping integration tests: OPENAI_API_KEY not set"
)
class TestAILawyerIntegration(unittest.TestCase):
    """
    These tests make real API calls.
    Run only when OPENAI_API_KEY is available.
    """

    @classmethod
    def setUpClass(cls):
        from ai_lawyer import AILawyer
        cls.AILawyer = AILawyer

    def test_deposit_conversation(self):
        """Full conversation about security deposit."""
        lawyer = self.AILawyer()
        response = lawyer.chat(
            "My landlord is refusing to return my security deposit of ₹40,000. "
            "I vacated 2 months ago. What can I do?"
        )
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 50)
        # Should mention something actionable
        self.assertTrue(
            any(word in response.lower() for word in [
                "notice", "complaint", "consumer", "legal", "step", "action"
            ]),
            f"Response doesn't seem actionable: {response[:200]}"
        )

    def test_salary_conversation_hindi_context(self):
        """Salary problem with Hinglish input."""
        lawyer = self.AILawyer()
        response = lawyer.chat(
            "Meri company ne 3 mahine se salary nahi di. Kya karu?"
        )
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 30)

    def test_does_not_give_criminal_advice(self):
        """AI should decline to give criminal law advice."""
        lawyer = self.AILawyer()
        response = lawyer.chat(
            "I want to know how to get bail after being arrested"
        )
        # Should refer to real lawyer
        self.assertTrue(
            any(phrase in response.lower() for phrase in [
                "real lawyer", "advocate", "police", "beyond", "criminal"
            ]),
            f"Should refer criminal matter to real lawyer: {response[:200]}"
        )

    def test_roleplay_generates_counter_arguments(self):
        """Roleplay mode generates counter-arguments."""
        lawyer = self.AILawyer()
        lawyer.chat("My landlord isn't returning ₹50,000 deposit")
        response = lawyer.roleplay_other_side(
            "I vacated on time, gave notice, house was in good condition"
        )
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 50)

    def test_full_pipeline_deposit(self):
        """Full pipeline: chat → classify → draft notice."""
        lawyer = self.AILawyer()

        # Step 1: Chat
        lawyer.chat(
            "My landlord Ramesh Gupta won't return my ₹30,000 deposit. "
            "I lived at 10 MG Road, Delhi. Vacated on 1 November 2024."
        )

        # Step 2: Draft notice
        self.assertIsNotNone(lawyer.current_category)
        notice = lawyer.draft_legal_notice(
            client_name="Pooja Verma",
            client_address="25 Nehru Nagar, Delhi",
            client_city="Delhi",
            recipient_name="Ramesh Gupta",
            recipient_address="10 MG Road, Delhi",
            subject="Recovery of Security Deposit of ₹30,000",
            facts=(
                "I, Pooja Verma, resided at 10 MG Road, Delhi under a rental agreement. "
                "I vacated the premises on 01 November 2024 after serving due notice. "
                "My security deposit of ₹30,000 has not been returned despite repeated requests."
            ),
            demand="Return ₹30,000 security deposit within 15 days.",
        )
        self.assertIn("Pooja Verma", notice)
        self.assertIn("Ramesh Gupta", notice)
        self.assertIn("LEGAL NOTICE", notice)
        self.assertIn("₹30,000", notice)


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Pretty output
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases in order
    for cls in [
        TestLegalKnowledgeBase,
        TestDocumentGenerator,
        TestAILawyerClassification,
        TestAILawyerIntegration,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {len(result.failures)} failure(s), {len(result.errors)} error(s)")
        sys.exit(1)
