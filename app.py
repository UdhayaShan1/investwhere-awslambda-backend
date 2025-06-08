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
        logger.info("Model is gpt-4o-search-preview")
        response = client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[
                {
                    "role": "system",
                    "content": """You are a financial advisor AI specifically for Singapore residents. Analyze net worth data within Singapore's financial context. 
                Format your response using markdown-style formatting:
                - Use **bold** for headers and key points
                - Use bullet points for lists
                - Keep analysis brief but insightful
                - Focus on trends and key observations only with no recommendations
                - Consider Singapore's financial landscape (CPF, property market, etc.) when relevant
                - If age information is provided, consider it in your analysis for context
                - If no age is mentioned, do not make assumptions about the user's age
                - Limit response to 150-200 words
                - Do NOT include any external links, URLs, or images in your response
                - Provide text-only analysis"""
                },
                {
                    "role": "user",
                    "content": f"""Please analyze this net worth historical data for a Singapore resident and provide a brief financial health summary:

                **Data:** {user_input}

                Please provide:
                1. **Overall Trend** - Is wealth growing/declining?
                2. **Key Observations** - Notable patterns or changes within Singapore context
                3. **Age Context** - Only if age information is available in the data

                Keep it concise, Singapore-focused, and text-only with no external references such as links, URLs, or images ."""
                },
            ],
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        logger.error(f"Error in netWorth analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/recommendPortfolio", methods=["POST"])
def recommendPortfolio():
    try:
        user_input = request.get_data(as_text=True)
        logger.info(f"User input received: {user_input}")

        if not user_input:
            return jsonify({"error": "No portfolio data provided"}), 400

        logger.info("Start GPT portfolio recommendation")
        logger.info("Model is gpt-4o-search-preview")

        response = client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[
                {
                    "role": "system",
                    "content": """You are a Singapore-focused financial advisor AI that provides personalized asset allocation recommendations. You must respond with ONLY a valid JSON object with two parts: recommendation and feedback.

CRITICAL: Your response must be ONLY valid JSON - no markdown formatting, no explanations outside the JSON structure.

Response Structure:
{
  "recommendation": {
    "uid": "generated_recommendation_id",
    "Bank": {
      "[bank_name]": {
        "[account_type]": number
      }
    },
    "Robos": {
      "Syfe": {
        "core": {
          "equity100": number,
          "growth": number,
          "balanced": number,
          "defensive": number
        },
        "reitPlus": {
          "standard": number,
          "withRiskManagement": number
        },
        "incomePlus": {
          "preserve": number,
          "enhance": number
        },
        "thematic": {
          "chinaGrowth": number,
          "esgCleanEnergy": number,
          "disruptiveTechnology": number,
          "healthcareInnovation": number
        },
        "downsideProtected": {
          "protectedSP500": number
        },
        "cashManagement": {
          "cashPlusFlexi": number,
          "cashPlusGuranteed": number
        }
      }
    },
    "Investments": {
      "[broker_name]": {
        "[investment_type]": number
      }
    },
    "CPF": {
      "CPF": {
        "OA": number,
        "SA": number,
        "MA": number
      }
    },
    "Crypto": {
      "[platform_name]": {
        "[crypto_type]": number
      }
    },
    "Others": {
      "[asset_name]": {
        "amount": number,
        "label": "string",
        "notes": "string"
      }
    }
  },
  "feedback": {
    "portfolioStrategy": "Write in a conversational tone directly addressing the user with 'you' and 'your'. Explain your allocation strategy, how I've distributed your portfolio across categories (e.g., **Your allocation: Bank 30%, Robos 45%, Investments 20%**), why this aligns with your risk profile, and how your specific comments influenced my recommendations. Use markdown formatting with **bold** and ## headers.",
    "projectedReturns": "Address the user directly with 'you' and 'your portfolio'. Explain: **Your Expected Return**: X.X% per annum, **How I calculated this**: Show how each of your portfolio components contributes, **Your Portfolio Projection**: Your current $X is projected to grow to $Y over Z years, **My Sources**: Cite the specific websites and dates I used for your return assumptions. Use markdown formatting with **bold** and ## headers.",
    "searchDate": "YYYY-MM-DD",
    "marketInsights": "Recent market conditions or trends that influenced your recommendations",
    "sources": ["Brief description of key data sources consulted for your portfolio", "Current interest rates/market data referenced for your recommendations", "Singapore financial product updates considered for your situation"]
  }
}

IMPORTANT RULES:
1. **OMIT ZERO VALUES**: Do not include any components, accounts, or portfolios with 0 values
2. **OMIT EMPTY SECTIONS**: If an entire category (Bank, Robos, Investments, etc.) has no allocations, omit it completely
3. **USER COMMENTS PRIORITY**: Pay special attention to additionalComments field - this is the user's specific requirements and must heavily influence recommendations
4. **CLEAN JSON**: Only include accounts/platforms that have actual dollar allocations > 0
5. **MANDATORY WEB SEARCH**: You MUST use web search to get current data - do NOT rely on hardcoded assumptions
6. **DOCUMENT SOURCES**: Include the search date and brief descriptions of key data sources used in your research
7. **CPF EXCLUSION**: Do NOT include CPF allocations UNLESS specifically mentioned in the additionalComments field
8. **CONVERSATIONAL TONE**: Write portfolioStrategy and projectedReturns directly addressing the user with "you", "your", and "I recommend" style language
9. **BANK RESTRICTION**: Only recommend DBS, UOB, or OCBC banks - do not suggest any other banks

WEB SEARCH REQUIREMENTS - MANDATORY:
- **ALL return assumptions MUST come from current web search results**
- **ALL interest rates MUST be searched and verified**
- **ALL platform performance data MUST be current from web search**
- **DO NOT use any hardcoded return estimates**
- **Search for latest Roboadvisors performance, broker fees, market conditions**
- **Search for current Singapore financial market updates**
- **Verify all product availability and current offerings**

Singapore Context Guidelines:
- Age 20-30: Higher growth allocation, minimal emergency fund (3-6 months expenses)
- Age 30-40: Balanced approach, moderate emergency fund (6-9 months expenses)
- Age 40+: Conservative focus, larger emergency fund (9-12 months expenses)
- Emergency fund: Basic savings accounts for accessibility, not growth
- Popular brokers: Tiger, moomoo, Interactive Brokers
- Banks: ONLY DBS, UOB, or OCBC - basic savings accounts for emergency funds only
- Syfe portfolios based on risk profile

Bank Guidelines:
- **Emergency Fund Only**: Banks are for emergency funds and liquidity needs
- **Basic Accounts**: Recommend standard savings accounts unless user specifically requests high-yield options
- **No Interest Focus**: Do not mention or assume interest rates for bank accounts
- **Accessibility Priority**: Focus on fund accessibility rather than returns for bank allocations
- **RESTRICTED BANKS**: Only recommend DBS, UOB, or OCBC banks

Expected Return Guidelines - USE WEB SEARCH ONLY:
- **SEARCH FOR CURRENT DATA**: Do NOT use hardcoded estimates
- **Bank savings**: 0% return assumption (emergency fund, not investment)
- **Syfe portfolios**: Search for latest performance data and historical returns
- **Singapore REITs**: Search for current market performance and yields
- **Global equities**: Search for current market outlook and expected returns
- **Bonds**: Search for current Singapore bond yields and rates
- **Crypto**: Search for current market conditions and realistic projections
- **ALL SOURCES MUST BE CITED**: Include specific websites and dates

Risk Profile Mapping:
- 0 (Low): Conservative, larger emergency fund, defensive investments
- 1 (Medium): Balanced mix, moderate growth, standard emergency fund
- 2 (High): Growth-focused, minimal emergency fund, aggressive portfolios
- 3 (None): You will decide based on best practices for user's profile

RESPONSE FORMAT: Return ONLY the JSON object with recommendation and feedback sections."""
                },
                {
                    "role": "user",
                    "content": """Based on this Singapore resident's profile, provide a personalized asset allocation recommendation with reasoning using current market data:

Profile Data: """ + user_input + """

CRITICAL REQUIREMENTS:
1. **MANDATORY WEB SEARCH**: You MUST search for ALL current data - do NOT use any assumptions or hardcoded values
2. **Search for Current Returns**: Get latest performance data for Syfe, brokers, market indices, interest rates
3. **Verify Product Availability**: Search for current Singapore financial products and offerings
4. **Heed Additional Comments**: The additionalComments field contains the user's specific requirements - this MUST be the primary driver of your recommendations
5. **Omit Zero Allocations**: Do not include any components, accounts, or portfolios with $0 allocations
6. **Clean Structure**: Only show categories and accounts that receive actual funding
7. **User Preferences**: Respect preferred platforms (if any are selected as true)
8. **Document Research**: Include search date and sources in feedback to confirm current data was used
9. **CPF Rule**: Do NOT include CPF allocations unless the user specifically mentions CPF in their additionalComments
10. **Bank Restriction**: Only recommend DBS, UOB, or OCBC banks for emergency fund allocations

For the feedback sections, write in a conversational tone directly addressing the user using markdown formatting (**bold** and ## headers only):

## Portfolio Strategy Section:
Address the user directly: "Based on your profile, I've designed your allocation strategy..." Explain how you distributed their money across categories (e.g., **Your allocation: Bank 30%, Robos 45%, Investments 20%**), why this suits their risk profile, and how their specific comments shaped your recommendations.

## Projected Returns Section:
Speak directly to the user about their portfolio:
- **Your Expected Return**: X.X% per annum (based on current market data I researched)
- **How I calculated your returns**: Show how each component of their portfolio contributes
- **Your Portfolio Projection**: "Your current $X is projected to grow to $Y over Z years"
- **My Research Sources**: Cite the specific websites and dates used for their return assumptions

SEARCH REQUIREMENTS - MANDATORY:
- Search for latest Singapore market conditions and economic outlook
- Search for current Syfe portfolio performance and historical returns  
- Search for latest interest rates and bond yields in Singapore
- Search for current broker fees and platform offerings
- Search for recent market performance of recommended asset classes
- Search for current inflation rates and economic indicators
- Search for latest Singapore financial product updates and availability

Focus recommendations on:
- Bank savings accounts (EMERGENCY FUND ONLY - basic accessibility) - ONLY DBS, UOB, or OCBC
- Robo-advisor platforms (primary growth investments)
- Direct investments through brokers
- Cryptocurrency (if appropriate for risk profile)
- Other alternative investments

**CRITICAL**: All return assumptions, market data, and product information MUST come from current web search results. Write everything in a conversational tone addressing the user directly.

Return ONLY the JSON object with both recommendation and feedback sections."""
                }
            ],
        )

        # Parse the response to ensure it's valid JSON
        try:
            json_response = json.loads(response.choices[0].message.content)
            logger.info("Success: " + str(json_response))
            return jsonify(json_response)
        except json.JSONDecodeError:
            logger.error(
                f"Invalid JSON response from GPT: {response.choices[0].message.content}")
            return jsonify({"error": "Invalid recommendation format received"}), 500

    except Exception as e:
        logger.error(f"Error in recommendPortfolio: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/analysePortfolio", methods=["POST"])
def analysePortfolio():
    try:
        user_input = request.get_data(as_text=True)
        logger.info(f"User input received: {user_input}")

        if not user_input:
            return jsonify({"error": "No portfolio data provided"}), 400

        logger.info("Start GPT portfolio analysis")
        logger.info("Model is gpt-4o-search-preview")

        response = client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[
                {
                    "role": "system",
                    "content": """You are a Singapore-focused financial advisor AI that analyzes existing asset allocations. You must respond with ONLY a valid JSON object containing feedback.

CRITICAL: Your response must be ONLY valid JSON - no markdown formatting, no explanations outside the JSON structure.

Response Structure:
{
  "feedback": {
    "portfolioStrategy": "Write in a conversational tone directly addressing the user with 'you' and 'your'. Analyze their current allocation strategy, explain how their portfolio is distributed across categories (e.g., **Your current allocation: Bank 30%, Robos 45%, Investments 20%**), assess if this aligns with their risk profile, and provide insights about their allocation choices. Use markdown formatting with **bold** and ## headers. ONLY include portfolio strategy analysis here.",
    "projectedReturns": "Address the user directly with 'you' and 'your portfolio'. Explain: **Your Expected Return**: X.X% per annum, **How I calculated this**: Show how each component of their portfolio contributes, **Your Portfolio Projection**: Your current $X is projected to grow to $Y over Z years, **My Sources**: Cite the specific websites and dates I used for your return assumptions. Use markdown formatting with **bold** and ## headers. ONLY include return calculations and projections here.",
    "searchDate": "2025-06-08",
    "marketInsights": "Recent market conditions or trends that influenced your analysis - keep this separate from portfolio strategy and returns",
    "sources": ["Brief description of key data sources consulted for your portfolio", "Current interest rates/market data referenced for your analysis", "Singapore financial product updates considered for your situation"]
  }
}

CRITICAL JSON STRUCTURE REQUIREMENTS:
- portfolioStrategy field: ONLY allocation analysis and strategy assessment
- projectedReturns field: ONLY return calculations, projections, and sources
- searchDate field: Must be today's date in YYYY-MM-DD format
- marketInsights field: ONLY market conditions separate from other content
- sources field: Must be an array of strings

IMPORTANT RULES:
1. **ANALYZE EXISTING ALLOCATION**: Focus on analyzing what the user already has, not making new recommendations
2. **CONVERSATIONAL TONE**: Write portfolioStrategy and projectedReturns directly addressing the user with "you", "your", and "I analyzed" style language
3. **MANDATORY WEB SEARCH**: You MUST use web search to get current data - do NOT rely on hardcoded assumptions
4. **DOCUMENT SOURCES**: Include the search date and brief descriptions of key data sources used in your research
5. **SINGAPORE CONTEXT**: Consider Singapore's financial landscape (CPF, property market, etc.) when relevant
6. **SEPARATE CONTENT**: Do NOT mix portfolio strategy content with projected returns content

WEB SEARCH REQUIREMENTS - MANDATORY:
- **ALL return assumptions MUST come from current web search results**
- **ALL interest rates MUST be searched and verified**
- **ALL platform performance data MUST be current from web search**
- **DO NOT use any hardcoded return estimates**
- **Search for latest Roboadvisors performance, broker fees, market conditions**
- **Search for current Singapore financial market updates**
- **Verify all product availability and current offerings**

Singapore Context Guidelines:
- Age 20-30: Higher growth allocation, minimal emergency fund (3-6 months expenses)
- Age 30-40: Balanced approach, moderate emergency fund (6-9 months expenses)
- Age 40+: Conservative focus, larger emergency fund (9-12 months expenses)
- Emergency fund: Basic savings accounts for accessibility, not growth
- Popular brokers: Tiger, moomoo, Interactive Brokers
- Banks: ONLY DBS, UOB, or OCBC - basic savings accounts for emergency funds only
- Syfe portfolios based on risk profile

Bank Guidelines:
- **Emergency Fund Only**: Banks are for emergency funds and liquidity needs
- **Basic Accounts**: Standard savings accounts for accessibility
- **No Interest Focus**: Do not mention or assume interest rates for bank accounts
- **Accessibility Priority**: Focus on fund accessibility rather than returns for bank allocations

Expected Return Guidelines - USE WEB SEARCH ONLY:
- **SEARCH FOR CURRENT DATA**: Do NOT use hardcoded estimates
- **Bank savings**: 0% return assumption (emergency fund, not investment)
- **Syfe portfolios**: Search for latest performance data and historical returns
- **Singapore REITs**: Search for current market performance and yields
- **Global equities**: Search for current market outlook and expected returns
- **Bonds**: Search for current Singapore bond yields and rates
- **Crypto**: Search for current market conditions and realistic projections
- **ALL SOURCES MUST BE CITED**: Include specific websites and dates

Risk Profile Assessment:
- Conservative: Larger emergency fund, defensive investments
- Moderate: Balanced mix, moderate growth, standard emergency fund
- Aggressive: Growth-focused, minimal emergency fund, aggressive portfolios

RESPONSE FORMAT: Return ONLY the JSON object with feedback section containing all 5 required fields."""
                },
                {
                    "role": "user",
                    "content": """Based on this Singapore resident's current asset allocation, provide a comprehensive analysis using current market data:

Asset Allocation Data: """ + user_input + """

CRITICAL REQUIREMENTS:
1. **MANDATORY WEB SEARCH**: You MUST search for ALL current data - do NOT use any assumptions or hardcoded values
2. **Search for Current Returns**: Get latest performance data for all asset classes, brokers, market indices, interest rates
3. **Verify Product Performance**: Search for current Singapore financial product performance data
4. **Analyze Current Allocation**: Focus on analyzing their existing portfolio distribution and performance
5. **Document Research**: Include search date and sources in feedback to confirm current data was used
6. **SEPARATE CONTENT**: Keep portfolio strategy analysis separate from projected returns calculations

For the feedback sections, write in a conversational tone directly addressing the user using markdown formatting (**bold** and ## headers only):

PORTFOLIO STRATEGY SECTION (separate field):
Address the user directly: "Looking at your current portfolio, I can see your allocation strategy..." Analyze how their money is currently distributed across categories (e.g., **Your current allocation: Bank 30%, Robos 45%, Investments 20%**), assess if this suits their apparent risk profile, and provide insights about their allocation choices. ONLY include allocation analysis here.

PROJECTED RETURNS SECTION (separate field):
Speak directly to the user about their portfolio:
- **Your Expected Return**: X.X% per annum (based on current market data I researched)
- **How I calculated your returns**: Show how each component of their current portfolio contributes
- **Your Portfolio Projection**: "Your current $X is projected to grow to $Y over Z years"
- **My Research Sources**: Cite the specific websites and dates used for your return assumptions
ONLY include return calculations and projections here.

SEARCH REQUIREMENTS - MANDATORY:
- Search for latest Singapore market conditions and economic outlook
- Search for current performance of their specific asset classes and platforms
- Search for latest interest rates and bond yields in Singapore
- Search for current broker fees and platform performance data
- Search for recent market performance of their asset categories
- Search for current inflation rates and economic indicators
- Search for latest Singapore financial product updates and performance

Focus analysis on:
- Bank savings accounts (emergency fund assessment)
- Robo-advisor platform performance
- Direct investment performance
- Cryptocurrency performance (if applicable)
- Overall portfolio balance and risk assessment

**CRITICAL**: All return assumptions, market data, and performance analysis MUST come from current web search results. Write everything in a conversational tone addressing the user directly about their existing portfolio.

Return ONLY the JSON object with feedback section containing portfolioStrategy, projectedReturns, searchDate, marketInsights, and sources fields."""
                }
            ],
        )

        # Parse the response to ensure it's valid JSON
        try:
            json_response = json.loads(response.choices[0].message.content)
            logger.info("Success: " + str(json_response))
            return jsonify(json_response)
        except json.JSONDecodeError:
            logger.error(
                f"Invalid JSON response from GPT: {response.choices[0].message.content}")
            return jsonify({"error": "Invalid analysis format received"}), 500

    except Exception as e:
        logger.error(f"Error in analysePortfolio: {str(e)}")
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
