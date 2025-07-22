import pandas as pd
import random
import requests
from collections import Counter
from datetime import datetime, timedelta

# --- Configuration for Sarvam API ---
# IMPORTANT: Replace "YOUR_SARVAM_API_KEY" with your actual key.
SARVAM_API_KEY = "sk_560q4ubw_4IG0YNBGzLXcAw33HjblFFFm"
# NOTE: This is an assumed API endpoint. Please replace with the actual URL from Sarvam's documentation.
SARVAM_API_URL = "https://api.sarvam.ai/v1/chat/completions" 

# ==============================================================================
# --- SentimentAgent Class ---
# This class handles all the data processing for the main dashboard.
# ==============================================================================
class SentimentAgent:
    def __init__(self, feedback_file_path):
        """
        Initializes the SentimentAgent by loading and processing the feedback data.
        """
        self.file_path = feedback_file_path
        self.df = self._load_data()

    def _load_data(self):
        """
        Loads the feedback data from the CSV file into a pandas DataFrame.
        """
        try:
            df = pd.read_csv(self.file_path)
            # Convert timestamp to datetime objects for easier manipulation
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except FileNotFoundError:
            print(f"Error: Feedback file not found at {self.file_path}")
            return pd.DataFrame() # Return an empty DataFrame if file not found
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()

    def _analyze_sentiment(self, feedback_text):
        """
        A simple rule-based sentiment analysis function.
        This can be replaced with a more sophisticated model if needed.
        """
        feedback_text = str(feedback_text).lower()
        if any(word in feedback_text for word in ['good', 'great', 'excellent', 'love', 'amazing', 'happy']):
            return 'Positive'
        elif any(word in feedback_text for word in ['bad', 'poor', 'terrible', 'hate', 'disappointed', 'issue']):
            return 'Negative'
        else:
            return 'Neutral'

    def get_dashboard_data(self):
        """
        This is the main method that processes the data and returns a dictionary
        containing all the necessary information for the dashboard.
        """
        # Reload data each time to get the latest feedback
        self.df = self._load_data()
        
        if self.df.empty:
            # Return default zeroed data if there's no feedback
            return {
                'total_messages': 0, 'positive': 0, 'negative': 0, 'neutral': 0,
                'engaged': 0, 'disengaged': 0, 'alerts': 0,
                'top_subjects': {}, 'messages': [], 
                'user_activity': {'dates': [], 'active': [], 'inactive': []},
                'sentiment': {'positive': 0, 'neutral': 0, 'negative': 0}
            }

        # --- Perform Sentiment Analysis ---
        # Apply the sentiment analysis to each feedback entry.
        self.df['sentiment'] = self.df['feedback'].apply(self._analyze_sentiment)

        # --- Calculate Key Metrics ---
        total_messages = len(self.df)
        sentiment_counts = self.df['sentiment'].value_counts()
        positive_sentiments = sentiment_counts.get('Positive', 0)
        negative_sentiments = sentiment_counts.get('Negative', 0)
        neutral_sentiments = sentiment_counts.get('Neutral', 0)

        # Engagement metrics (based on rating)
        engaged = self.df[self.df['rating'] >= 4].shape[0]
        disengaged = self.df[self.df['rating'] <= 2].shape[0]
        
        # Top complaint subjects (from negative feedback)
        negative_feedback = self.df[self.df['sentiment'] == 'Negative']
        top_subjects = Counter(negative_feedback['subject']).most_common(5)

        # --- User Activity Over Last 7 Days ---
        activity_data = {'dates': [], 'active': [], 'inactive': []}
        today = datetime.now().date()
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            formatted_date = date.strftime('%b %d')
            
            # Count users who gave feedback on this day
            active_users = self.df[self.df['timestamp'].dt.date == date]['user_id'].nunique()
            
            # For this example, 'inactive' could be total unique users minus active ones
            total_unique_users = self.df['user_id'].nunique()
            inactive_users = total_unique_users - active_users

            activity_data['dates'].append(formatted_date)
            activity_data['active'].append(active_users)
            activity_data['inactive'].append(inactive_users)
            
        # --- Prepare Data for Frontend ---
        dashboard_data = {
            'total_messages': total_messages,
            'positive': int(positive_sentiments),
            'negative': int(negative_sentiments),
            'neutral': int(neutral_sentiments),
            'engaged': int(engaged),
            'disengaged': int(disengaged),
            'alerts': int(negative_sentiments), # Using negative sentiments as a proxy for alerts
            'top_subjects': dict(top_subjects),
            'messages': self.df.sort_values(by='timestamp', ascending=False).to_dict('records'),
            'user_activity': activity_data,
            # This nested sentiment dict is required by app.py
            'sentiment': {
                'positive': int(positive_sentiments),
                'neutral': int(neutral_sentiments),
                'negative': int(negative_sentiments)
            }
        }
        
        return dashboard_data
