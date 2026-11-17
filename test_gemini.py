from services.ai_assistant import ask_gemini

question = "Explain PM2.5 in simple words."

print("\nConnecting to Gemini AI...")

response = ask_gemini(question)

print("\nGemini AI Response:\n")
print(response)