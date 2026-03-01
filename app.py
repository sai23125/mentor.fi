from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import json
import re

app = Flask(__name__)

# Paste your Groq API key here
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


SYSTEM_PROMPT = """You are Mentor.AI — an elite business intelligence system backed by 35+ years of market data, Wall Street analysis, Silicon Valley startup patterns, and emerging market insights.

CRITICAL: Respond with ONLY a valid JSON object. No text before or after. No markdown. No backticks. Just raw JSON.

Use this exact structure:

{"title":"Short title max 8 words","analysis":"Full advice with all 7 sections using **bold** for headers: 📊 Market Pulse, 💡 3 Business Ideas, ⚖️ Truth Table, 💰 Money Reality, 🗓️ 7-Day War Room, ⚠️ Risk Matrix, 🎯 Mentor.AI Verdict. Be detailed, specific and brutally honest.","charts":{"investment":{"label":"Investment Breakdown","items":[{"name":"Equipment","amount":15000,"color":"#00F5A0"},{"name":"Marketing","amount":8000,"color":"#00D9F5"},{"name":"Operations","amount":5000,"color":"#7B61FF"},{"name":"Emergency Fund","amount":3000,"color":"#FF6B6B"},{"name":"Misc","amount":2000,"color":"#FFB347"}],"currency":"₹","total_label":"Total Investment"},"revenue":{"label":"Revenue Projection 12 Months","months":["M1","M2","M3","M4","M5","M6","M7","M8","M9","M10","M11","M12"],"pessimistic":[0,0,5000,10000,15000,20000,25000,30000,35000,40000,45000,50000],"realistic":[0,2000,8000,18000,30000,45000,60000,75000,90000,105000,120000,140000],"optimistic":[0,5000,18000,40000,70000,105000,145000,185000,225000,265000,305000,350000],"currency":"₹"},"risks":{"label":"Risk Matrix","items":[{"name":"Market Competition","probability":70,"impact":80,"mitigation":"Differentiate on quality and service"},{"name":"Cash Flow Issues","probability":55,"impact":90,"mitigation":"Maintain 3 month emergency fund"},{"name":"Customer Acquisition","probability":65,"impact":75,"mitigation":"Start with referrals and word of mouth"},{"name":"Regulatory Risk","probability":25,"impact":85,"mitigation":"Consult a local business lawyer"},{"name":"Burnout","probability":60,"impact":70,"mitigation":"Set clear work hours from day one"}]},"timeline":{"label":"7-Day Action Plan","days":[{"day":1,"title":"Market Research","description":"Research your top 3 competitors online. Note their prices, strengths and weaknesses.","category":"research"},{"day":2,"title":"Validate the Idea","description":"Talk to 10 potential customers. Ask if they would pay for your solution.","category":"validation"},{"day":3,"title":"Build MVP Plan","description":"Sketch out the simplest version of your product or service you can launch.","category":"build"},{"day":4,"title":"First Outreach","description":"Contact 5 potential customers or partners. Offer a free trial or discount.","category":"outreach"},{"day":5,"title":"Financial Plan","description":"Create a simple spreadsheet with startup costs and break-even point.","category":"financial"},{"day":6,"title":"Setup Basics","description":"Register your business name, create a social media profile, get a UPI ID.","category":"build"},{"day":7,"title":"Review and Commit","description":"Review everything. Set your official launch date. Tell 3 people about your business.","category":"review"}]}}}

Adjust ALL numbers to be realistic for the user's specific capital and situation."""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"success": False, "error": "No input provided"}), 400

    raw = ""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Give me business advice for: {user_input}"}
            ],
            max_tokens=3000,
            temperature=0.7
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'^```\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        raw = raw.strip()

        # Extract JSON object
        start = raw.find('{')
        end = raw.rfind('}') + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        data = json.loads(raw)
        return jsonify({"success": True, "data": data})

    except json.JSONDecodeError:
        return jsonify({
            "success": True,
            "data": {
                "title": "Mentor.AI Business Advice",
                "analysis": raw or "Could not parse response. Please try again.",
                "charts": default_charts()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def default_charts():
    return {
        "investment": {"label":"Investment Breakdown","items":[{"name":"Equipment","amount":15000,"color":"#00F5A0"},{"name":"Marketing","amount":8000,"color":"#00D9F5"},{"name":"Operations","amount":5000,"color":"#7B61FF"},{"name":"Emergency Fund","amount":3000,"color":"#FF6B6B"},{"name":"Misc","amount":2000,"color":"#FFB347"}],"currency":"₹","total_label":"Total Investment"},
        "revenue": {"label":"Revenue Projection","months":["M1","M2","M3","M4","M5","M6","M7","M8","M9","M10","M11","M12"],"pessimistic":[0,0,5000,10000,15000,20000,25000,30000,35000,40000,45000,50000],"realistic":[0,2000,8000,18000,30000,45000,60000,75000,90000,105000,120000,140000],"optimistic":[0,5000,18000,40000,70000,105000,145000,185000,225000,265000,305000,350000],"currency":"₹"},
        "risks": {"label":"Risk Matrix","items":[{"name":"Competition","probability":70,"impact":80,"mitigation":"Differentiate on quality"},{"name":"Cash Flow","probability":55,"impact":90,"mitigation":"Keep 3 months emergency fund"},{"name":"Customer Acquisition","probability":65,"impact":75,"mitigation":"Start with referrals"},{"name":"Regulatory","probability":25,"impact":85,"mitigation":"Consult a lawyer"},{"name":"Burnout","probability":60,"impact":70,"mitigation":"Set work boundaries early"}]},
        "timeline": {"label":"7-Day Action Plan","days":[{"day":1,"title":"Research","description":"Research competitors.","category":"research"},{"day":2,"title":"Validate","description":"Talk to customers.","category":"validation"},{"day":3,"title":"Plan MVP","description":"Plan your launch.","category":"build"},{"day":4,"title":"Outreach","description":"Contact 5 leads.","category":"outreach"},{"day":5,"title":"Finances","description":"Plan your budget.","category":"financial"},{"day":6,"title":"Setup","description":"Register and setup.","category":"build"},{"day":7,"title":"Launch","description":"Set launch date.","category":"review"}]}
    }


if __name__ == "__main__":
    app.run(debug=True)
