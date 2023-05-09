from flask import Flask, render_template, request, session
from questions import questions
import random

app = Flask(__name__)

#Setting variables for keeping track of the users score in solo study
asked_q = []
score = [0]
current_q = None

# This route takes the user to the homepage
@app.route('/')
def index():
    return render_template('index.html')

# This route takes the user to the solo study section of the website
@app.route('/quiz', )
def solo_study():
    # Setting the appropriate values for keeping track of the score
    asked_q.clear()
    score.clear()
    score.append(0)
    random.shuffle(questions)
    return render_template('solo.html')

# This route takes the user to the question part of the test page
# https://radiusofcircle.blogspot.com/2016/03/making-quiz-website-with-python.html
# This helped inspire the functionality, but I had to modify what they suggested
# a ton to make it work with our program
@app.route('/test', methods=['GET'])
def test():
    if request.method == 'GET':        
        # Iterate through the questions to get the last
        q_idx = 0
        question_obj = questions[q_idx]
        question = question_obj["question"]
        while question in asked_q:
            q_idx += 1
            question_obj = questions[q_idx]
            question = question_obj["question"]

        # add the question to the list of asked questions and pull relevant info
        asked_q.append(question)
        choices = question_obj["choices"]
        answer = question_obj["answer"]
        hints = question_obj["hints"]

        return(render_template('test.html', question = question, choices = choices, answer = answer, hints = hints))
    
# This route shows the user a page showing their results for the previous question
@app.route('/result', methods=['POST'])
def results():
    # Check if user is at the end of the questions
    end = False
    if len(asked_q) == len(questions):
        end = True

    # Gets the users response https://stackoverflow.com/questions/31662681/flask-handle-form-with-radio-buttons 
    user_ans = request.form.get('options')
    user_ans = user_ans[0]
    choices = []
    hints = []

    # Gets the last question that was asked
    question = asked_q[len(asked_q)-1]

    #This goes through the questions and grabs the actual answer for the last question asked
    for i in range(len(questions)):
        question_obj = questions[i]
        if question_obj['question'] == question:
            real_ans = question_obj['answer']
            for choice in question_obj['choices']:
                choices.append(choice)
            for hint in question_obj['hints']:
                hints.append(hint)
            break
    
    # If the user got the correct answer, increment their score by one
    if user_ans == real_ans:
        result = "correct!"
        score.append(get_score() + 1)
    else:
        result = "incorrect"
    
    # So that full word is printed on the results page
    if user_ans == "T":
        user_ans = "True"
    elif user_ans == "F":
        user_ans = "False"

    return render_template('results.html', correct = get_score(), total_qs = len(questions), qs_asked = len(asked_q), 
                           percent = get_percentage(), real_answer = real_ans, result = result, question = question, 
                           choices = choices, answer = user_ans, hints = hints, end = end)

@app.route('/quiz_end', methods=['GET'])
def quiz_end():
    return(render_template('quiz_end.html', correct = get_score(), total_qs = len(asked_q), percent = get_percentage()))

# This route takes the user to the class game page 
@app.route('/game')
def class_game():
    return render_template('game.html')

# This route takes the user to the admin login page
@app.route('/admin')
def admin():

    return render_template('admin.html')

# Function to keep track of users score in solo quiz
# Code Citation: https://stackoverflow.com/questions/18516891/how-do-i-keep-track-of-score-increments-in-python
# Accessed 5/5/2023
def get_score():
    return score[len(score)-1]

def get_percentage():
    if len(asked_q) != 0:
        percent = get_score() / int(len(asked_q)) * 100
        return int(percent)
    else:
        return 0

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)