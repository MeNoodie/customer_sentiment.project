import csv
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect
from sentiment_agent import SentimentAgent
from suggestion_agent import SuggestionAgent

# --- Configuration ---
# Define file paths in one place for easy management.
FEEDBACK_FILE = r"C:\code.folder\New folder\sentiment_agent\application_\main_app\feedback.csv"
SOLUTIONS_FILE = r"C:\code.folder\New folder\sentiment_agent\application_\main_app\complaints_solutions.csv" # Assuming this is the path for your solutions file

# --- App Initialization ---
app = Flask(__name__)

# --- Agent Initialization ---
# Create a single instance of each agent when the app starts.
# This is much more efficient than re-loading the files on every request.
try:
    sentiment_agent = SentimentAgent(FEEDBACK_FILE)
    suggestion_agent = SuggestionAgent(FEEDBACK_FILE)
except FileNotFoundError as e:
    print(f"FATAL ERROR: Could not find data file: {e}. Please check the file paths in the configuration section.")
    # In a real app, you might exit or handle this more gracefully.
    sentiment_agent = None
    suggestion_agent = None


# --- Integrated Feedback Saver ---
# Merged from your feedback_handler.py for simplicity.
def save_feedback(type_, rating, subject, feedback, source="Web"):
    """
    Saves a new feedback entry to the CSV file.
    """
    fields = ['timestamp', 'source', 'type', 'rating', 'subject', 'feedback', 'user_id'] # Added user_id for better tracking

    # Generate a timestamp for the feedback
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create the row data as a dictionary
    row = {
        'timestamp': timestamp,
        'source': source,
        'type': type_,
        'rating': int(rating) if rating else 0,
        'subject': subject,
        'feedback': feedback,
        'user_id': request.remote_addr # Use IP as a simple user identifier
    }

    try:
        # Open the file in append mode
        with open(FEEDBACK_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            # Write the header only if the file is empty
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        print(f"Error writing feedback to {FEEDBACK_FILE}: {e}")


# --- Main Dashboard and API Routes ---

@app.route("/")
def dashboard():
    """
    Main route to display the dashboard. It fetches fresh data from the agent.
    """
    if not sentiment_agent:
        return "Error: Sentiment Agent not initialized. Please check server logs.", 500
    
    # ==============================================================================
    # --- FIX APPLIED HERE ---
    # Removed the call to `sentiment_agent.refresh_data()` because the SentimentAgent
    # class does not have this method. This was causing the AttributeError.
    # The data is processed by the get_dashboard_data() method itself.
    # ==============================================================================
    original_data = sentiment_agent.get_dashboard_data()

    # Structure the data for the template
    data_for_template = original_data.copy()
    data_for_template['sentiment'] = {
        'positive': original_data.get('positive', 0),
        'neutral': original_data.get('neutral', 0),
        'negative': original_data.get('negative', 0)
    }
    
    return render_template("insights.html", data=data_for_template)


@app.route("/api/sentiments")
def api_sentiments():
    """
    API endpoint to provide dashboard data as JSON, used by the charts.
    """
    if not sentiment_agent:
        return jsonify({"error": "Sentiment Agent not initialized."}), 500

    # ==============================================================================
    # --- FIX APPLIED HERE ---
    # Also removed the unnecessary `refresh_data()` call from the API endpoint.
    # ==============================================================================
    data = sentiment_agent.get_dashboard_data()
    return jsonify(data)

# --- LIZA AI Chatbot API Routes ---

@app.route("/api/suggestions")
def api_suggestions():
    """
    API endpoint for the LIZA AI chatbot to get initial, proactive suggestions.
    """
    if not suggestion_agent:
        return jsonify({"error": "Suggestion Agent not initialized."}), 500
    suggestions = suggestion_agent.get_suggestions()
    return jsonify({"suggestions": suggestions})

@app.route("/api/liza-chat", methods=["POST"])
def liza_chat():
    """
    API endpoint to handle a user's message to the LIZA AI and get a relevant reply.
    """
    if not suggestion_agent:
        return jsonify({"error": "Suggestion Agent not initialized."}), 500
        
    user_msg = request.json.get("message", "")
    if not user_msg:
        replies = [suggestion_agent.get_initial_greeting()]
    else:
        replies = suggestion_agent.get_suggestions(user_msg)
        
    return jsonify({"replies": replies})


# --- Feedback Submission Routes ---

@app.route("/submit-feedback", methods=["GET", "POST"])
def handle_web_feedback():
    """
    Handles both displaying the feedback form and submitting it.
    """
    if request.method == "POST":
        data = request.get_json()
        save_feedback(
            type_=data.get("type", "product"),
            rating=int(data.get("rating", 3)),
            subject=data.get("subject", "Feedback"),
            feedback=data.get("feedback", ""),
            source="Product Page"
        )
        return jsonify({'status': 'success', 'message': 'Feedback received!'})
    return render_template("index.html")

@app.route("/submit-ticket", methods=["GET", "POST"])
def handle_ticket_feedback():
    """
    Handles both displaying the ticket form and submitting it.
    """
    if request.method == "POST":
        save_feedback(
            type_=request.form['type'],
            rating=int(request.form['rating']),
            subject=request.form['subject'],
            feedback=request.form['description'],
            source="Ticket"
        )
        return redirect("/")
    return render_template("ticket.html")

@app.route("/send-email-support", methods=["GET", "POST"])
def handle_email_feedback():
    """
    Handles both displaying the email form and submitting it.
    """
    if request.method == "POST":
        save_feedback(
            type_=request.form['type'],
            rating=int(request.form['rating']),
            subject=request.form['subject'],
            feedback=request.form['description'],
            source="Email"
        )
        return redirect("/")
    return render_template("email.html")

@app.route("/dashboard_alt")
def dashboard_alt():
    return render_template("insights.html")


if __name__ == "__main__":
    app.run(debug=True)
