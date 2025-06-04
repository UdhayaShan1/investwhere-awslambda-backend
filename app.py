from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv
import json
import logging

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI()

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@app.route("/")
def index():
    return "Lambda Hello World"


@app.route("/analyseNetWorth", methods=["POST"])
def netWorth():
    try:
        # Get JSON data instead of raw data
        user_input = request.get_data()
        logger.info(f"User input received: {user_input}")

        if not user_input:
            return jsonify({"error": "No net worth data provided"}), 400

        logger.info("Start GPT analysis")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a financial advisor AI. Analyze net worth data and provide concise, actionable insights. 
                    Format your response using markdown-style formatting:
                    - Use **bold** for headers and key points
                    - Use bullet points for lists
                    - Keep analysis brief but insightful
                    - Focus on trends, key observations, and 1-2 actionable recommendations
                    - Limit response to 150-200 words"""
                },
                {
                    "role": "user",
                    "content": f"""Please analyze this net worth historical data and provide a brief financial health summary:

**Data:** {user_input}

Please provide:
1. **Overall Trend** - Is wealth growing/declining?
2. **Key Observations** - Notable patterns or changes
3. **Quick Recommendation** - One actionable insight

Keep it concise and easy to read at a glance."""
                },
            ],
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        logger.error(f"Error in netWorth analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/ask-ai", methods=["POST"])
def ask():
    print("LOL", request.json)
    user_input = request.json.get("question", "")
    if not user_input:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Updated way to call the ChatCompletion API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input},
            ],
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)
