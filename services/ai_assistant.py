
import os

from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Get Gemini API key
API_KEY = os.getenv("GEMINI_API_KEY")


def ask_gemini(question, air_quality_data=None):

    if not API_KEY:
        return "Gemini API key is missing. Please check your .env file."

    try:
        client = genai.Client(api_key=API_KEY)

        context = ""

        if air_quality_data:
            context = f"""
            Current air quality measurements:
            {air_quality_data}
            """

        prompt = f"""
        You are an expert Urban Air Quality Assistant.

        Explain air pollution in simple language
        and provide practical, evidence-based precautions.

        {context}

        User question:
        {question}

        Give a clear, helpful answer.
        Do not invent air quality measurements.
        Mention uncertainty where appropriate.
        Do not present your response as a medical diagnosis.
        """

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config={
                "http_options": {
                    "timeout": 90000
                }
            }
        )

        return response.text or "No response received from Gemini."

    except Exception as e:
        return f"Gemini API error: {e}"
