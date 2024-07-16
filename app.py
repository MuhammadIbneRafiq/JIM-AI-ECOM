from flask import Flask, render_template, request, jsonify
# from mult_agent_langflow import *
app = Flask(__name__)

@app.get('/')
def index_get():
    return render_template('base.html')

@app.post('/predict')
def predict():
    text = request.get_json().get('message')
    # try and catch
    response = 'this is groq"s response' # use the api from multi_agent 
    message = {'answer': response}
    return jsonify(message)

if __name__ == '__main__':
    app.run(debug=True)

