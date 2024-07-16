from langchain_groq import ChatGroq
import os
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from typing import List, Dict
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_LLM = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama3-70b-8192"
)

class AIEcommerceAgent():
    def categorize_email(self, summary):
        prompt = PromptTemplate(
            template="""system
            You are an e-commerce ai chatbot categorization agent. Categorize the following text into one of the following categories: 'product_inquiry', 'price_inquiry', 'order_status', 'customer_complaint', 'customer_feedback', or 'off_topic'.
            Email content:\n\n {chat_history} \n\n
            assistant""",
            input_variables=["chat_history"],
        )

        categorizing_agent = prompt | GROQ_LLM | JsonOutputParser()
        result = categorizing_agent.invoke({"chat_history": summary})
        return result['category']

    def draft_reply(self, initial_email, email_category):
        draft_writer_prompt = PromptTemplate(
            template="""system
            You are an e-commerce customer service agent. Based on the text category and the content of the initial text, draft a thoughtful and friendly reply.

            If the customer email is 'off_topic' then ask them questions to get more information.
            If the customer email is 'customer_complaint' then try to assure we value them and that we are addressing their issues.
            If the customer email is 'customer_feedback' then try to assure we value them and that we are addressing their issues.
            If the customer email is 'product_inquiry' then try to provide the information they requested in a succinct and friendly way.
            If the customer email is 'price_inquiry' then try to provide the pricing information they requested.
            If the customer email is 'order_status' then try to provide the order status information.

            Always reply in 1 short sentence

            user
            INITIAL_MESSAGE: {initial_email} \n
            EMAIL_CATEGORY: {email_category} \n
            assistant""",
            input_variables=["initial_email", "email_category"],
        )

        draft_writer_chain = draft_writer_prompt | GROQ_LLM | JsonOutputParser()
        return draft_writer_chain.invoke({"initial_email": initial_email, "email_category": email_category})

class GraphState(TypedDict):
    initial_email: str
    email_category: str
    draft_email: str
    final_email: str
    num_steps: int

def categorize_email(state):
    initial_email = state['initial_email']
    num_steps = int(state['num_steps'])
    num_steps += 1
    
    email_category = AIEcommerceAgent().categorize_email(initial_email)
    return {"email_category": email_category, "num_steps": num_steps}

def draft_email_writer(state):
    initial_email = state["initial_email"]
    email_category = state["email_category"]
    num_steps = state['num_steps']
    num_steps += 1

    draft_email = AIEcommerceAgent().draft_reply(initial_email, email_category)
    email_draft = draft_email['email_draft']

    return {"draft_email": email_draft, "num_steps": num_steps}

def route_to_rewrite(state):
    return "no_rewrite"

def run_graph(EMAIL):
    workflow = StateGraph(GraphState)

    workflow.add_node("categorize_email", categorize_email) # categorize email
    workflow.add_node("draft_email_writer", draft_email_writer)

    workflow.set_entry_point("categorize_email")
    workflow.add_edge("categorize_email", "draft_email_writer")
    workflow.add_edge("draft_email_writer", END)

    app = workflow.compile()
    inputs = {"initial_email": EMAIL, "num_steps": 0}
    output = app.invoke(inputs)

    return output['draft_email']

EMAIL = """yo hey do u know the price of soap
"""
response = run_graph(EMAIL)
print(response)
