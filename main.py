from flask import Flask, render_template, request, session, redirect, url_for
from questions import questions
import random
from google.cloud import datastore
import constants
from game_images import game_images

app = Flask(__name__)
client = datastore.Client()
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

    # reset score and image index to 0
    global image_index
    global game_score
    image_index = 0
    game_score = 0

    # shuffle images
    random.shuffle(game_images)

    return render_template('game.html')
def play_game():

    global image_index
    global game_score
    
    # Use GET method to show image
    if request.method == "GET":
        # Exit game and show results after all images have been shown
        if image_index == len(game_images):
            return render_template('game_results.html', score=game_score, questions=len(game_images))
        
        # Otherwise show next image
        else:
            image_url = game_images[image_index]["image"]
            hint = game_images[image_index]["hint"]
            return render_template('game_play.html', image=image_url, hint=hint)
        

    # Use POST method to show result
    if request.method == "POST":
        # end var to control which button to show on results page (if game is over)
        end = False
        if request.form["category"] == game_images[image_index]["answer"]:
            game_score += 1
            result = "Correct!"
        else:
            result = "Incorrect."
        # increment image_index after result is determined
        image_index += 1
        if image_index == len(game_images):
            end = True
        return render_template('matching_result.html', score=game_score, questions=image_index, result=result, end=end)

@app.route('/play', methods=["GET", "POST"])
def play_game():

    global image_index
    global game_score
    
    # Use GET method to show image
    if request.method == "GET":
        # Exit game and show results after all images have been shown
        if image_index == len(game_images):
            return render_template('game_results.html', score=game_score, questions=len(game_images))
        
        # Otherwise show next image
        else:
            image_url = game_images[image_index]["image"]
            hint = game_images[image_index]["hint"]
            return render_template('game_play.html', image=image_url, hint=hint)
        

    # Use POST method to show result
    if request.method == "POST":
        # end var to control which button to show on results page (if game is over)
        end = False
        if request.form["category"] == game_images[image_index]["answer"]:
            game_score += 1
            result = "Correct!"
        else:
            result = "Incorrect."
        # increment image_index after result is determined
        image_index += 1
        if image_index == len(game_images):
            end = True
        return render_template('matching_result.html', score=game_score, questions=image_index, result=result, end=end)        
# This route takes the user to the admin login page
@app.route('/admin')
def admin():
    query = client.query(kind=constants.questions)
    results = list(query.fetch())
    q_list = []
    for e in results:
        q_list.append(str(e["question"]))
    return render_template('admin.html',q_list=q_list)

@app.route('/addq')
def add_page():
    return render_template('addq.html')

@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        content = request.form
        #parsing the form to format the data properly
        question = content['question']
        #choices string parsing
        choices_str = str(content['choices'])
        choices = []
        choice = ''
        counter = 0
        for i in choices_str:
            if i == ',':
                choices.append(choice)
                counter += 1
                choice=''
                continue
            choice += i
            counter += 1
            if counter == len(choices_str):
                choices.append(choice)
        #answer parsing
        answer = content['answer']
        #week parsing
        week = content['week']
        #Image string parsing
        img_str = str(content['image'])
        images = []
        image = ''
        counter = 0
        for i in img_str:
            if i == ',':
                images.append(image)
                image=''
                counter += 1
                continue
            image += i
            counter += 1
            if counter == len(img_str):
                images.append(image)

        # adding question to database based on parsed data
        new_q = datastore.entity.Entity(key=client.key(constants.questions))
        new_q.update({"question": question, "choices": choices,
          "answer": answer, "week": week, "image": images} )
        client.put(new_q)
        return redirect(url_for('admin'))

@app.route('/editq')
def edit_page():
    query = client.query(kind=constants.questions)
    results = list(query.fetch())
    q_list = []
    for e in results:
        q_list.append(str(e["question"]))
    if len(q_list) == 0:
        return redirect(url_for('admin'))
    return render_template('editq.html', q_list=q_list)

@app.route('/edit', methods=['POST'])
def edit():
    if request.method == 'POST':
        query = client.query(kind=constants.questions)
        results = list(query.fetch())
        db_question = request.form['question_to_edit']
        for e in results:

            if str(e["question"]) == str(db_question):
                q_key = client.key(constants.questions, int(e.key.id))
                print(q_key)
                q_to_edit = client.get(key=q_key)
        content = request.form
        #parsing the form to format the data properly
        question = content['question']
        #choices string parsing
        choices_str = str(content['choices'])
        choices = []
        choice = ''
        counter = 0
        for i in choices_str:
            if i == ',':
                choices.append(choice)
                counter += 1
                choice=''
                continue
            choice += i
            counter += 1
            if counter == len(choices_str):
                choices.append(choice)
        #answer parsing
        answer = content['answer']
        #week parsing
        week = content['week']
        #Image string parsing
        img_str = str(content['image'])
        images = []
        image = ''
        counter = 0
        for i in img_str:
            if i == ',':
                images.append(image)
                image=''
                counter += 1
                continue
            image += i
            counter += 1
            if counter == len(img_str):
                images.append(image)

        # adding question to database based on parsed data

        q_to_edit.update({"question": question, "choices": choices,
          "answer": answer, "week": week, "image": images} )
        client.put(q_to_edit)
    return redirect(url_for('admin'))

@app.route('/deleteq')
def delete_page():
    query = client.query(kind=constants.questions)
    results = list(query.fetch())
    q_list = []
    for e in results:
        q_list.append(str(e["question"]))
    if len(q_list) == 0:
        return redirect(url_for('admin'))
    return render_template('deleteq.html', q_list=q_list)

@app.route('/delete', methods=["POST"])
def delete():
    print("here")
    content= request.form['question']

    if request.method == 'POST':
        query = client.query(kind=constants.questions)
        results = list(query.fetch())
        content = request.form['question']
        for e in results:
            if str(e["question"]) == str(content):
                q_key = client.key(constants.questions, int(e.key.id))
                client.delete(q_key)
                return redirect(url_for('admin'))

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