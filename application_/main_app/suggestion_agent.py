import pandas as pd
import random
import requests

# --- Configuration for Sarvam AI ---
# IMPORTANT: Replace "YOUR_SARVAM_API_KEY" with your actual key.
SARVAM_API_KEY = "sk_560q4ubw_4IG0YNBGzLXcAw33HjblFFFm"
# NOTE: This is an assumed API endpoint. Please replace with the actual URL from Sarvam's documentation.
SARVAM_API_URL = "https://api.sarvam.ai/v1/chat/completions" 

class SuggestionAgent:
    def __init__(self, feedback_file_path, solutions_file_path=None):
        """
        Initializes the SuggestionAgent.
        - feedback_file_path: Path to the main feedback.csv file.
        - solutions_file_path: Optional path to a file with pre-defined solutions for the AI.
        """
        self.feedback_df = None
        self.solutions_df = None
        
        try:
            self.feedback_df = pd.read_csv(feedback_file_path)
            if 'subject' in self.feedback_df.columns:
                self.feedback_df['subject'] = self.feedback_df['subject'].astype(str)
            if 'timestamp' in self.feedback_df.columns:
                self.feedback_df['timestamp'] = pd.to_datetime(self.feedback_df['timestamp'], errors='coerce')
        except FileNotFoundError:
            print(f"Warning: Could not find feedback file at {feedback_file_path}.")

        if solutions_file_path:
            try:
                self.solutions_df = pd.read_csv(solutions_file_path)
            except FileNotFoundError:
                print(f"Warning: Could not find solutions file at {solutions_file_path}.")

    def get_initial_greeting(self):
        """
        Provides a random friendly greeting for the chatbot.
        """
        greetings = [
            "Hi there! I'm LIZA, your AI assistant. How can I assist you today?",
            "Hello! I'm LIZA. What can I do for you?",
        ]
        return random.choice(greetings)

    # ==============================================================================
    # --- CHOOSE YOUR SUGGESTION METHOD ---
    # Use either the local method (faster) or the API method (smarter).
    # Your app.py should call this `get_suggestions` method.
    # ==============================================================================
    def get_suggestions(self, user_query=""):
        # --- Option 1: Use Local Suggestions (Fast, Offline) ---
        # return self.get_suggestions_local(user_query)
        
        # --- Option 2: Use AI-Powered Suggestions (Smarter, Requires API) ---
        return self.get_suggestions_api(user_query)

    # ==============================================================================
    # --- METHOD 1: Local Rule-Based Suggestions ---
    # ==============================================================================
    def get_suggestions_local(self, user_query=""):
        """
        Finds relevant past feedback from feedback.csv to provide suggestions.
        """
        if self.feedback_df is None or self.feedback_df.empty:
            return ["I'm sorry, I don't have any data to reference at the moment."]

        if not user_query:
            negative_feedback = self.feedback_df[self.feedback_df['rating'] <= 2]
            if not negative_feedback.empty:
                top_complaints = negative_feedback['subject'].value_counts().nlargest(3).index.tolist()
                if top_complaints:
                    return [f"I can see we've had some reports about: {', '.join(top_complaints)}. Can I help with one of these topics or something else?"]
            return ["How can I help you today?"]

        query_keywords = set(user_query.lower().split())
        matching_rows = self.feedback_df[self.feedback_df['subject'].str.lower().apply(
            lambda subj: any(key in subj for key in query_keywords)
        )]

        if matching_rows.empty:
            return ["I couldn't find any specific information related to your query. I will log your feedback for the team. Could you please rephrase or provide more details?"]

        positive_matches = matching_rows[matching_rows['rating'] >= 4].copy()
        if not positive_matches.empty:
            most_recent_positive = positive_matches.sort_values('timestamp', ascending=False).iloc[0]
            return [f"I found some positive feedback that might be related. One user said: '{most_recent_positive['feedback']}'. I hope this helps!"]

        negative_matches = matching_rows[matching_rows['rating'] <= 2].copy()
        if not negative_matches.empty:
            most_common_subject = negative_matches['subject'].mode()[0]
            return [f"I see other users have also reported issues regarding '{most_common_subject}'. Your feedback is valuable, and I will be sure to log this for our team to review."]

        return ["Thank you for your feedback. I have logged it for our team to review."]

    # ==============================================================================
    # --- METHOD 2: AI-Powered Suggestions via Sarvam API ---
    # ==============================================================================
    def get_suggestions_api(self, user_query=""):
        """
        Provides suggestions by calling the Sarvam LLM.
        """
        if not user_query:
            if self.solutions_df is not None and not self.solutions_df.empty:
                top_complaints = self.solutions_df.head(3)
                return [row['solution'] for index, row in top_complaints.iterrows()]
            else:
                return ["How can I assist you with product or service issues?"]

        headers = {
            "Authorization": f"Bearer {SARVAM_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = "You are LIZA, a friendly and helpful customer support AI. Your goal is to help users with their issues. Be concise and clear in your answers."
        
        if self.solutions_df is not None:
            known_issues_context = "\nHere is some context on known issues and their solutions:\n" + self.solutions_df.to_string()
            system_prompt += known_issues_context

        data = {
            "model": "sarvam/open-llm-v1", # Replace with the correct Sarvam model name
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
        }

        try:
            response = requests.post(SARVAM_API_URL, headers=headers, json=data, timeout=20)
            response.raise_for_status()
            
            api_response = response.json()
            return [api_response['choices'][0]['message']['content'].strip()]
            
        except requests.exceptions.RequestException as e:
            print(f"API Error getting suggestion for '{user_query}': {e}")
            return ["I'm having a little trouble connecting right now. Please try again in a moment."]
