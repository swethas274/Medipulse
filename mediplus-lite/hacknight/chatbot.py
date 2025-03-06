import json
import numpy as np
import joblib
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from textblob import TextBlob
from flask import Flask, render_template, request, session
from datetime import datetime

# Configure Gemini
genai.configure(api_key='AIzaSyDQtd7b_sXfg0L495CQ8gdz5fNirGL7uiU')

# Initialize Gemini model with correct version
model_gemini = genai.GenerativeModel('gemini-2.0-flash')

def analyze_sentiment(text):
    """Analyze sentiment using TextBlob."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    return 'Positive' if polarity > 0 else 'Negative' if polarity < 0 else 'Neutral'

# Sample Data for ML Model
X_train = ["I feel anxious", "I'm happy", "I have panic attacks", "I am relaxed"]
y_train = ["Anxiety", "Normal", "Panic Attack", "Normal"]

vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)

# Train ML Model
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)
joblib.dump((vectorizer, model), 'chatbot_model.pkl')

def get_ml_prediction(user_input):
    """Predict user's mental state using ML model."""
    vectorizer, model = joblib.load('chatbot_model.pkl')
    input_tfidf = vectorizer.transform([user_input])
    return model.predict(input_tfidf)[0]

def get_gemini_response(user_input):
    """Generate a detailed, human-like response using Gemini API with better error handling."""
    safe_prompt = f"""As a supportive listener, I'm here to chat about well-being and daily life challenges.
    The person said: {user_input}
    Provide a friendly, supportive response focusing on general well-being and positive thinking.
    Avoid medical advice or clinical terms. Keep the response encouraging and general."""
    
    try:
        response = model_gemini.generate_content(safe_prompt)
        
        # Debug info
        print("\nAPI Response Debug Info:")
        print(f"Response object: {response}")
        print(f"Prompt Feedback: {response.prompt_feedback}")
        
        # Check for blocked content
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
            print(f"Content blocked. Reason: {response.prompt_feedback.block_reason}")
            return "I want to be helpful while keeping our chat friendly and general. Could you rephrase that or tell me more about what's on your mind?"
        
        # Check for valid response
        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
        
        return "I'm here to listen and chat. Would you like to tell me more about your day?"
        
    except Exception as e:
        print(f"\nGemini API Debug Error:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return "I'm having a moment. Let's continue our chat in a general way about how you're feeling."

def chatbot(user_input):
    """Enhanced chatbot function with better error handling."""
    try:
        sentiment = analyze_sentiment(user_input)
        category = get_ml_prediction(user_input)
        ai_response = get_gemini_response(user_input)
        
        # Build response with fallbacks
        response_parts = []
        response_parts.append(f"Mood: {sentiment}")
        
        if category in ["Anxiety", "Panic Attack", "Normal"]:
            response_parts.append(f"Focus area: {category}")
        
        response_parts.append(ai_response)
        
        # Add helpful tips based on category
        if category == "Anxiety":
            response_parts.append("\nTip: Let's try a simple breathing exercise together.")
        elif category == "Panic Attack":
            response_parts.append("\nTip: Let's focus on the present moment together.")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return "I'm here to chat and listen. Would you like to share what's on your mind?"

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management

@app.route("/", methods=["GET", "POST"])
def home():
    # Initialize chat history in session if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    if request.method == "POST":
        user_input = request.form["message"]
        
        try:
            # Get chatbot response
            bot_response = chatbot(user_input)
            
            # Add messages to chat history
            session['chat_history'].append({'type': 'user', 'text': user_input, 'time': datetime.now()})
            session['chat_history'].append({'type': 'bot', 'text': bot_response, 'time': datetime.now()})
            
            # Keep only last 50 messages
            if len(session['chat_history']) > 50:
                session['chat_history'] = session['chat_history'][-50:]
            
            session.modified = True
            
        except Exception as e:
            print(f"Error in chat processing: {str(e)}")
            session['chat_history'].append({
                'type': 'bot', 
                'text': "I apologize, but I'm having trouble processing that right now. Could you try rephrasing?",
                'time': datetime.now()
            })
    
    return render_template("index.html", chat_history=session['chat_history'])

if __name__ == "__main__":
    # Remove test code and replace with Flask app run
    app.run(debug=True, port=5000)
