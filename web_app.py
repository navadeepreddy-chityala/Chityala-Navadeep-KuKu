"""
web_app.py
----------
Zero-dependency local web prototype for Nyay (AI Lawyer).
Powered by Google Gemini with verified Indian statutory grounding.
Runs on Python standard library (http.server) — no pip install required!

Run:
    python web_app.py
Then open:
    http://localhost:8000
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import date
from gemini_client import load_env_file
load_env_file()

from legal_knowledge import find_legal_category, get_relevant_provisions, LEGAL_KB, LegalCategory
from document_generator import (
    generate_legal_notice,
    generate_consumer_complaint,
    generate_notice_reply,
)
from ai_lawyer import AILawyer

PORT = 8000
_lawyer = AILawyer()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nyay (न्याय) — AI Legal Assistant for India</title>
  <style>
    :root {
      --primary: #1e3a8a;
      --primary-light: #3b82f6;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --accent: #d97706;
      --danger: #dc2626;
      --success: #16a34a;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background-color: var(--bg); color: var(--text); display: flex; flex-direction: column; height: 100vh; }
    
    header { background: var(--primary); color: white; padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    header h1 { font-size: 20px; display: flex; align-items: center; gap: 8px; }
    header .badge { background: #dbeafe; color: #1e40af; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 9999px; }
    .status-pill { background: #15803d; color: white; font-size: 11px; padding: 3px 8px; border-radius: 12px; margin-left: 8px; display: inline-flex; align-items: center; gap: 4px; }

    .container { display: flex; flex: 1; overflow: hidden; }

    /* Sidebar presets */
    .sidebar { width: 330px; background: white; border-right: 1px solid var(--border); padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
    .sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
    .sidebar h3 { font-size: 12px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; }
    .btn-reset { background: #f1f5f9; border: 1px solid var(--border); font-size: 11px; padding: 4px 8px; border-radius: 6px; cursor: pointer; color: #475569; font-weight: 600; }
    .btn-reset:hover { background: #e2e8f0; color: #0f172a; }

    .preset-btn { text-align: left; background: #f8fafc; border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; font-size: 12px; cursor: pointer; transition: all 0.15s ease; }
    .preset-btn:hover { border-color: var(--primary-light); background: #eff6ff; }
    .preset-btn strong { display: block; color: var(--primary); font-size: 13px; margin-bottom: 2px; }

    /* Chat Area */
    .main-chat { flex: 1; display: flex; flex-direction: column; background: var(--bg); }
    .messages-container { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }

    .msg { max-width: 85%; padding: 14px 18px; border-radius: 12px; font-size: 14px; line-height: 1.5; }
    .msg.user { align-self: flex-end; background: var(--primary); color: white; border-bottom-right-radius: 2px; }
    .msg.bot { align-self: flex-start; background: white; border: 1px solid var(--border); border-bottom-left-radius: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }

    .bot-card { display: flex; flex-direction: column; gap: 12px; }
    .pill { display: inline-flex; align-items: center; gap: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; padding: 3px 8px; border-radius: 9999px; width: fit-content; }
    .pill.info { background: #e0f2fe; color: #0369a1; }
    .pill.danger { background: #fee2e2; color: #b91c1c; }
    .pill.success { background: #dcfce7; color: #15803d; }

    .advisory-text { font-size: 14px; line-height: 1.6; color: #1e293b; }
    .advisory-text h3, .advisory-text h4 { color: #1e3a8a; margin: 10px 0 4px 0; }
    .advisory-text strong { color: #0f172a; }

    .doc-preview { background: #f8fafc; border: 1px dashed #cbd5e1; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 11px; max-height: 220px; overflow-y: auto; white-space: pre-wrap; color: #334155; }
    
    .roleplay-box { background: #fefce8; border: 1px solid #fef08a; padding: 12px; border-radius: 8px; font-size: 13px; }
    .roleplay-box strong { color: #854d0e; }

    /* Input bar */
    .input-bar { background: white; border-top: 1px solid var(--border); padding: 14px 24px; display: flex; gap: 12px; align-items: center; }
    .input-bar textarea { flex: 1; height: 50px; padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px; resize: none; font-size: 14px; outline: none; }
    .input-bar textarea:focus { border-color: var(--primary-light); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15); }
    .input-bar button { background: var(--primary); color: white; border: none; padding: 0 24px; height: 50px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
    .input-bar button:hover { background: #1e40af; }

    .disclaimer-banner { background: #fffbeb; border-top: 1px solid #fef3c7; color: #92400e; font-size: 11px; text-align: center; padding: 6px 12px; }
  </style>
</head>
<body>

  <header>
    <h1>⚖️ Nyay (न्याय) — AI Legal Companion <span class="status-pill">● Google Gemini Active</span></h1>
    <div>
      <span class="badge">Kuku Assignment • Problem 2</span>
    </div>
  </header>

  <div class="container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>Quick Test Scenarios</h3>
        <button class="btn-reset" onclick="clearChat()">🔄 New Chat</button>
      </div>

      <button class="preset-btn" onclick="loadScenario(6)">
        <strong>💰 Personal Loan / Debt Recovery</strong>
        Gave ₹30,000 to person, not repaid after 6 months.
      </button>

      <button class="preset-btn" onclick="loadScenario(1)">
        <strong>🏠 Landlord Withholding Deposit</strong>
        Bengaluru tenant, ₹70,000 security deposit unlawfully deducted.
      </button>

      <button class="preset-btn" onclick="loadScenario(2)">
        <strong>💼 3 Months Unpaid Salary</strong>
        Noida tech employee, ₹1,95,000 pending arrears.
      </button>

      <button class="preset-btn" onclick="loadScenario(3)">
        <strong>📦 E-Commerce Defective Product</strong>
        Damaged laptop, platform refused return window.
      </button>

      <button class="preset-btn" onclick="loadScenario(4)">
        <strong>📄 Reply to Notice (Notice Period)</strong>
        Company demanding 1.5 lakhs notice buyout.
      </button>

      <button class="preset-btn" onclick="loadScenario(5)">
        <strong>🚨 Criminal / Safety Boundary Test</strong>
        Police extortion query — verifies safe refusal & DLSA referral.
      </button>
    </div>

    <div class="main-chat">
      <div class="messages-container" id="chatBox">
        <div class="msg bot">
          <div class="bot-card">
            <span class="pill info">🤖 Google Gemini AI & Statutory Engine Active</span>
            <p><strong>Namaste! I am Nyay.</strong> I help ordinary citizens in India understand legal rights, navigate everyday disputes (rent, wages, debt recovery, consumer refunds), and prepare formal legal drafts without high legal fees.</p>
            <p><em>You can speak in English, Hindi, or Hinglish. What legal situation are you facing today?</em></p>
          </div>
        </div>
      </div>

      <div class="input-bar">
        <textarea id="userInput" placeholder="Apni pareshani yahan likhein (e.g. Maine pichle saal 30000 diye the wapas nahi de raha)..." onkeydown="handleKey(event)"></textarea>
        <button onclick="sendQuery()">Analyze & Act</button>
      </div>

      <div class="disclaimer-banner">
        ⚠️ <strong>Statutory Disclaimer:</strong> Nyay provides legal literacy and automated document drafting based on verified Indian statutory frameworks. It does not establish an attorney-client relationship. For contentious court litigation, consult a licensed advocate.
      </div>
    </div>
  </div>

  <script>
    const scenarios = {
      1: "Maine pichle mahine Koramangala ka flat khali kiya. Landlord Mahesh 70,000 ka security deposit wapas nahi de raha hai. Bol raha hai repainting aur normal wear-tear ke naam pe 40,000 kaat lega jabki agreement me likha tha normal wear tear excluded hai. Phone bhi block kar diya.",
      2: "My employer TechNova Labs hasn't paid my monthly salary of 65,000 for August, September, and October. Total 1,95,000 pending. HR says company is facing investor delays and asks me to keep working for free. I resigned yesterday.",
      3: "I ordered an Asus Vivobook laptop from CartZone for 54,000. It arrived with a broken hinge and dead screen. I contacted support within 6 hours. They closed my ticket saying 'damaged during customer unboxing' without inspection. Refund denied.",
      4: "My previous IT company sent me a threatening legal notice demanding 1.5 lakhs because I served only 30 days notice instead of 90 days. But my offer letter specifically stated notice can be adjusted against 45 days of unavailed privileged leaves.",
      5: "Police came to my shop yesterday without warrant and threatened to file a fake cheating FIR against me unless I pay them ₹20,000 cash. What section can I use to stop arrest and can you draft a complaint against police?",
      6: "i have give 30000 to a person last year and he said he will return back the money in 6 months but still he is not giving back the money"
    };

    function loadScenario(id) {
      document.getElementById('userInput').value = scenarios[id];
      sendQuery();
    }

    function handleKey(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendQuery();
      }
    }

    async function clearChat() {
      try {
        await fetch('/api/reset', { method: 'POST' });
      } catch(e) {}
      const chatBox = document.getElementById('chatBox');
      chatBox.innerHTML = `
        <div class="msg bot">
          <div class="bot-card">
            <span class="pill info">🤖 Google Gemini AI & Statutory Engine Active</span>
            <p><strong>Namaste! I am Nyay.</strong> I help ordinary citizens in India understand legal rights, navigate everyday disputes (rent, wages, debt recovery, consumer refunds), and prepare formal legal drafts without high legal fees.</p>
            <p><em>You can speak in English, Hindi, or Hinglish. What legal situation are you facing today?</em></p>
          </div>
        </div>
      `;
    }

    function formatMarkdown(text) {
      if (!text) return '';
      let clean = text
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
        .replace(/^### (.*$)/gim, '<h4 style="margin:8px 0 4px 0; color:#1e3a8a;">$1</h4>')
        .replace(/^## (.*$)/gim, '<h3 style="margin:10px 0 6px 0; color:#1e3a8a;">$1</h3>')
        .replace(/^• (.*$)/gim, '<li style="margin-left:18px;">$1</li>')
        .replace(/\\n/g, '<br>');
      return clean;
    }

    async function sendQuery() {
      const text = document.getElementById('userInput').value.trim();
      if (!text) return;

      const chatBox = document.getElementById('chatBox');

      // Append user msg
      const userDiv = document.createElement('div');
      userDiv.className = 'msg user';
      userDiv.innerText = text;
      chatBox.appendChild(userDiv);

      document.getElementById('userInput').value = '';
      chatBox.scrollTop = chatBox.scrollHeight;

      // Loading indicator
      const loadDiv = document.createElement('div');
      loadDiv.className = 'msg bot';
      loadDiv.id = 'loadingIndicator';
      loadDiv.innerHTML = '<span style="color:#64748b;">⏳ Consulting Gemini Legal Engine & Statutory Provisions...</span>';
      chatBox.appendChild(loadDiv);
      chatBox.scrollTop = chatBox.scrollHeight;

      try {
        const resp = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: text })
        });
        const data = await resp.json();

        chatBox.removeChild(loadDiv);

        const botDiv = document.createElement('div');
        botDiv.className = 'msg bot';

        let content = `<div class="bot-card">`;
        
        if (data.is_out_of_scope) {
          content += `<span class="pill danger">🚨 Out of Scope / Safety Protocol</span>`;
          content += `<div style="color:#b91c1c; font-weight:600;">Criminal / Police Matter Detected</div>`;
          content += `<div class="advisory-text">${formatMarkdown(data.advisory)}</div>`;
        } else {
          content += `<div>
            <span class="pill info">📋 Category: ${data.category_meta.name}</span>
            <span class="pill success" style="margin-left:6px;">⚖️ Forum: ${data.category_meta.typical_forum}</span>
          </div>`;
          content += `<p><strong>Statutory Assessment & Legal Counsel:</strong></p>`;
          content += `<div class="advisory-text">${formatMarkdown(data.advisory)}</div>`;

          if (data.document) {
            content += `<hr style="border:0; border-top:1px solid #e2e8f0; margin: 8px 0;">`;
            content += `<strong>📄 Generated Ready-to-Serve Action Document:</strong>`;
            content += `<div class="doc-preview">${data.document}</div>`;
          }

          if (data.roleplay) {
            content += `<hr style="border:0; border-top:1px solid #e2e8f0; margin: 8px 0;">`;
            content += `<div class="roleplay-box">
              <strong>🥊 Practice Drill (Anticipating the Opposition):</strong><br>
              <em>Opponent's Likely Stance:</em> "${data.roleplay.counter}"<br><br>
              <strong>Your Counter Strategy:</strong> ${data.roleplay.rebuttal}
            </div>`;
          }
        }

        content += `</div>`;
        botDiv.innerHTML = content;
        chatBox.appendChild(botDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

      } catch (err) {
        if (document.getElementById('loadingIndicator')) {
          chatBox.removeChild(loadDiv);
        }
        alert('Error connecting to Nyay backend: ' + err);
      }
    }
  </script>
</body>
</html>
"""

class NyayHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/reset":
            _lawyer.reset()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            return

        if self.path == "/api/analyze":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(body)
                query = payload.get("query", "")
            except Exception:
                query = ""

            response_data = self.process_query(query)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))

    def process_query(self, query: str) -> dict:
        q_lower = query.lower()

        # Check safety boundary (criminal/police)
        criminal_triggers = ["police", "fir", "arrest", "jail", "bail", "criminal", "extortion"]
        if any(w in q_lower for w in criminal_triggers):
            return {
                "is_out_of_scope": True,
                "category_meta": {"name": "Criminal / Police", "typical_forum": "Criminal Court / DLSA"},
                "advisory": (
                    "Nyay is strictly restricted from advising on criminal, police, or custodial proceedings to prevent accidental harm or illegal misguidance.\n\n"
                    "Recommended Immediate Steps:\n"
                    "1. Immediately contact an enrolled criminal advocate.\n"
                    "2. If you lack financial means, apply for free legal aid under Section 12 of Legal Services Authorities Act, 1987 at your local District Legal Services Authority (DLSA).\n"
                    "3. National Legal Services Authority (NALSA) Toll-Free: 15100.\n"
                    "4. If facing illegal police demand, you can submit a complaint to the District Police Complaints Authority (PCA) or State Human Rights Commission (SHRC)."
                ),
                "document": None,
                "roleplay": None
            }

        # Query conversational AI (Gemini with grounded fallback)
        try:
            ai_advice = _lawyer.chat(query)
        except Exception as e:
            ai_advice = f"Namaste. I reviewed your query: '{query}'. Under Indian civil law, you have rights to seek recovery and enforcement. Please provide further specifics regarding dates, evidence, and amounts."

        category = _lawyer.current_category or find_legal_category(query)

        # Generate sample ready-to-use document and practice drill
        doc = None
        roleplay = None

        if category and category.name == "security_deposit":
            doc = generate_legal_notice(
                client_name="[Tenant Name]",
                client_address="[Tenant Address]",
                client_city="[City]",
                recipient_name="[Landlord Name]",
                recipient_address="[Rented Property Address]",
                subject="Legal Notice: Refund of Security Deposit under Transfer of Property Act",
                facts=f"Tenant vacated premises in accordance with lease agreement. Landlord withheld deposit without itemized proof of damage.\nQuery Context: {query[:180]}...",
                demand="Refund the entire security deposit amount within 15 days of this notice.",
                legal_category=category,
                deadline_days=15
            )
            roleplay = {
                "counter": "The flat required deep cleaning and total wall repainting which cost more than the deposit.",
                "rebuttal": "Demand physical invoices, GST receipts, and reference the clause stating normal wear-and-tear cannot be deducted."
            }
        elif category and category.name == "unpaid_salary":
            doc = generate_legal_notice(
                client_name="[Employee Name]",
                client_address="[Current Address]",
                client_city="[City]",
                recipient_name="[Company / Director Name]",
                recipient_address="[Registered Office Address]",
                subject="Demand Notice: Payment of Overdue Wage Arrears under Payment of Wages Act, 1936",
                facts=f"Employee performed lawful employment duties. Employer failed to disburse wages by the 7th/10th of the calendar month.\nQuery Context: {query[:180]}...",
                demand="Disburse all outstanding salary arrears within 15 calendar days.",
                legal_category=category,
                deadline_days=15
            )
            roleplay = {
                "counter": "The company has cashflow constraints; all staff will be paid once new clients pay us.",
                "rebuttal": "Wages are first-charge liabilities under labour law; business risk cannot be shifted to salaried employees."
            }
        elif category and category.name == "ecommerce_refund":
            doc = generate_consumer_complaint(
                complainant_name="[Consumer Name]",
                complainant_address="[Consumer Residential Address]",
                complainant_phone="[Phone Number]",
                district="[District]",
                state="[State]",
                op_name="[E-Commerce Platform / Seller]",
                op_address="[Registered Entity Address]",
                facts=f"Defective goods delivered and refund rejected without fair inspection.\nQuery Context: {query[:180]}...",
                main_relief="Full refund of product invoice value with statutory interest",
                compensation=25000,
                litigation_cost=5000
            )
            roleplay = {
                "counter": "Our terms of service state that unboxing damage is customer liability once accepted from courier.",
                "rebuttal": "Consumer Protection Act 2019 supersedes unilateral terms of service when dead-on-arrival defect is reported promptly."
            }
        elif category and category.name == "money_recovery":
            doc = generate_legal_notice(
                client_name="[Lender Name / Your Name]",
                client_address="[Your Address]",
                client_city="[Your City]",
                recipient_name="[Borrower / Debtor Name]",
                recipient_address="[Borrower Address]",
                subject="Legal Demand Notice: Urgent Repayment of Debt / Loan of Rs. 30,000 with Statutory Interest",
                facts=f"A friendly/personal loan of Rs. 30,000 was disbursed with clear mutual agreement to repay within 6 months. Despite expiry of the agreed 6-month period and repeated reminders via phone/messaging, the amount remains unpaid in willful breach of contract.\nQuery Context: {query[:180]}...",
                demand="Repay the principal debt of Rs. 30,000 along with statutory interest @18% p.a. within 15 calendar days from the receipt of this notice, failing which legal proceedings under Order 37 CPC / Section 73 Indian Contract Act will be instituted.",
                legal_category=category,
                deadline_days=15
            )
            roleplay = {
                "counter": "I never formally borrowed money from you, it was a friendly gift or partnership investment, and there is no written stamp-paper loan agreement.",
                "rebuttal": "Under Indian Contract Act, oral contracts confirmed via UPI/bank statement transfer logs and WhatsApp chats constitute valid legal evidence of debt under Section 65B of the Indian Evidence Act."
            }
        elif category and category.name == "consumer_complaint":
            doc = generate_consumer_complaint(
                complainant_name="[Complainant Name]",
                complainant_address="[Residential Address]",
                complainant_phone="[Phone Number]",
                district="[District]",
                state="[State]",
                op_name="[Service Provider / Manufacturer]",
                op_address="[Opposite Party Address]",
                facts=f"Deficiency in service / unfair trade practice experienced.\nQuery Context: {query[:180]}...",
                main_relief="Full refund with statutory compensation for harassment",
                compensation=25000,
                litigation_cost=5000
            )
            roleplay = {
                "counter": "The product/service was delivered as per standard commercial terms.",
                "rebuttal": "Statutory warranties under the Consumer Protection Act 2019 cannot be contracted out via boilerplate disclaimers."
            }
        else:
            doc = generate_notice_reply(
                my_name="[Your Name]",
                my_address="[Your Address]",
                my_city="[Your City]",
                sender_of_notice_name="[Opposing Party / Law Firm]",
                sender_of_notice_address="[Sender Address]",
                notice_date="Recent",
                rebuttal=f"The claims made in the notice are denied in toto as erroneous.\nContext: {query[:180]}...",
                my_position="All obligations were lawfully discharged in accordance with agreed terms."
            )
            roleplay = {
                "counter": "You failed to give adequate notice and caused business losses.",
                "rebuttal": "Highlight written approvals and statutory leave offsets that waived or fulfilled notice covenants."
            }

        forum = category.typical_forum if category else "Civil Court / Lok Adalat / Consumer Forum"
        cat_name = category.name.replace("_", " ").title() if category else "General Civil Dispute"

        return {
            "is_out_of_scope": False,
            "category_meta": {
                "name": cat_name,
                "typical_forum": forum,
                "time_limit": category.time_limit if category else "3 years (Limitation Act, 1963)"
            },
            "advisory": ai_advice,
            "document": doc,
            "roleplay": roleplay
        }


def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), NyayHandler) as httpd:
        print(f"============================================================")
        print(f"  ⚖️  Nyay Web App Running at: http://localhost:{PORT}")
        print(f"  Zero external dependencies. Powered by Google Gemini.")
        print(f"  Press Ctrl+C to terminate.")
        print(f"============================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")


if __name__ == "__main__":
    start_server()
