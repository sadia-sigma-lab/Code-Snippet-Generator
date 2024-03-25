from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_session import Session
# import openai
# GOOGLE_API_KEY = 'AIzaSyC09MDUgjmY1-uKNS03dM5TT--TMGfFZ44'
import google.generativeai as genai
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
print("GOOGLE_API_KEY" , GOOGLE_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
VALID_LANGUAGES = ['Python', 'JavaScript', 'Java', 'C#', 'C++']

def sanitize_input(user_input):
    # Remove potentially harmful characters or patterns
    return user_input.replace("<", "").replace(">", "").replace("&", "")

app = Flask(__name__)
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        user_input = request.form.get('description')
        user_input = sanitize_input(user_input)
        language = request.form.get('language')
        print("langauage" , language)
        print("user_input", user_input)
        
        if not language:
            return "Please select a programming language.", 400
        if language not in VALID_LANGUAGES:
            return "Invalid programming language selected.", 400
        full_prompt = f"Language: {language}\nDescription: {user_input}\nNote: Include detailed comments in the code."

        # full_prompt = f"Act as code snippet generator for selected Programming language,  Validate language selected by the user if it is valid programming language"\
        "respond accordingly to the greetings as well"\
        "Language selected by current user: \n'{language} '\n"\
        "Request from current user: \n'{user_input}'\n" \
        "If this is a code snippet generation request for selected language programming language, " \
        "generate the code with detailed comments. If it's a general question other than code generation just ploitely say you'r responsibe for code snippets generation, " 
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(full_prompt)
            snippet = response.text
        except Exception as e:
            print(f"Error while generating response: {e}")
            snippet = "Error generating response."

        snippet_id = str(uuid.uuid4())
        session['history'].append({'id': snippet_id, 'prompt': user_input, 'snippet': snippet})
        session.modified = True

        return redirect(url_for('home'))

    return render_template('index.html', history=session['history'])

@app.route('/clear', methods=['POST'])
def clear_history():
    session['history'] = []  # Clear the history
    session.modified = True  # Mark the session as modified
    return redirect(url_for('home'))

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    snippet_id = data.get('snippetId')
    feedback = data.get('feedback')
    # Process the feedback here (e.g., save to database or log for analysis)
    print(f"Received feedback: {feedback} for snippet ID: {snippet_id}")
    return jsonify({"success": True, "message": "Feedback received"})

@app.route('/delete-snippet', methods=['POST'])
def delete_snippet():
    snippet_id = request.form.get('snippet_id')
    if 'history' in session:
        session['history'] = [item for item in session['history'] if item['id'] != snippet_id]
        session.modified = True
    return redirect(url_for('home'))


if __name__ == '__main__':
   
    app.run(debug=True)
