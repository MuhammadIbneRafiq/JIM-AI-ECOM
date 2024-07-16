from flask_cors import CORS

from flask import Flask, render_template, request, jsonify
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_LLM = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama3-70b-8192"
)
def generate_response(user_message):
    prompt = PromptTemplate(
        template="""system
        You are a customer service chatbot for an e-commerce store. Help the customer with their queries in a friendly and concise manner.
        Always reply under 1 sentence

        user
        Customer message: {message}

        assistant
        """,
        input_variables=["message"],
    )

    chat_agent = prompt | GROQ_LLM | StrOutputParser()
    response = chat_agent.invoke({"message": user_message})
    return response

@app.get('/')
def index_get():
    return render_template('base.html')

@app.post('/predict')
def predict():
    text = request.get_json().get('message')
    # try and catch
    response = generate_response(text) # use the api from multi_agent 
    message = {'answer': response}
    return jsonify(message)

if __name__ == '__main__':
    app.run(debug=True)

