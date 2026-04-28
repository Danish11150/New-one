from flask import Flask, render_template, jsonify, request
from agents.ceo import ceo_agent
from agents.trend_hunter import trend_hunter_agent
from agents.content_writer import content_writer_agent
from agents.seo_expert import seo_expert_agent
from agents.image_agent import image_agent
from agents.editor import editor_agent
from agents.social_media import social_media_agent
from agents.marketing import marketing_agent
from utils.blogger import publish_to_blogger
import threading
import os

app = Flask(__name__)

company_state = {
    "running": False,
    "logs": [],
    "results": {},
    "status": "standby"
}

def log(agent, message, status="working"):
    company_state["logs"].append({
        "agent": agent,
        "message": message,
        "status": status
    })

def run_company():
    company_state["running"] = True
    company_state["logs"] = []
    company_state["results"] = {}
    company_state["status"] = "running"
    try:
        log("CEO", "Aaj ke tasks assign kar raha hoon...")
        ceo_plan = ceo_agent()
        company_state["results"]["ceo"] = ceo_plan
        log("CEO", "Plan ready!", "done")

        log("Trend Hunter", "Trending topics dhundh raha hoon...")
        trend = trend_hunter_agent()
        company_state["results"]["trend"] = trend
        log("Trend Hunter", "Topic mila!", "done")

        log("Content Writer", "Blog post likh raha hoon...")
        post = content_writer_agent(trend)
        company_state["results"]["post"] = post
        log("Content Writer", "Blog post ready!", "done")

        log("SEO Expert", "SEO optimize kar raha hoon...")
        seo = seo_expert_agent(post["title"], post["content"])
        company_state["results"]["seo"] = seo
        log("SEO Expert", "SEO complete!", "done")

        log("Image Agent", "Post ke liye image bana raha hoon...")
        image_url = image_agent(post["title"])
        company_state["results"]["image"] = image_url
        log("Image Agent", "Image ready!", "done")

        log("Editor", "Post review kar raha hoon...")
        final_post = editor_agent(post, seo, image_url)
        company_state["results"]["final_post"] = final_post
        log("Editor", "Post approved!", "done")

        log("Social Media", "Captions bana raha hoon...")
        captions = social_media_agent(post["title"], post["content"])
        company_state["results"]["captions"] = captions
        log("Social Media", "Captions ready!", "done")

        log("Marketing", "Promotion strategy bana raha hoon...")
        marketing = marketing_agent(post["title"])
        company_state["results"]["marketing"] = marketing
        log("Marketing", "Strategy ready!", "done")

        log("CEO", "Blogger pr publish kar raha hoon...")
        publish_result = publish_to_blogger(final_post, image_url)
        company_state["results"]["published"] = publish_result
        log("CEO", "Post published! Kaam mukammal ho gaya!", "done")

        company_state["status"] = "completed"
    except Exception as e:
        log("System", f"Error aaya: {str(e)}", "error")
        company_state["status"] = "error"
    company_state["running"] = False

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/run", methods=["POST"])
def run():
    if company_state["running"]:
        return jsonify({"error": "Team pehle se kaam kar rahi hai!"}), 400
    thread = threading.Thread(target=run_company)
    thread.daemon = True
    thread.start()
    return jsonify({"message": "Company chalu ho gayi!"})

@app.route("/status")
def get_status():
    return jsonify(company_state)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
