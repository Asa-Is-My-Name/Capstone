from flask import Flask, render_template, request, session, redirect, url_for
import random
from google.cloud import datastore
import constants
from game_images import game_images
import os
import time

app = Flask(__name__)
client = datastore.Client()


# set a secret key (to use for sessions)
app.secret_key = os.urandom(24)


# This route takes the user to the homepage
@app.route('/')
def index():
    session.clear()
    # Use session to prevent access to the Admin section without password
    session['admin'] = False
    return render_template('index.html')


# Handling internal server error (which seems to only happen when taking quiz)
@app.errorhandler(500)
def internal_error(error):
    # redirect to end of quiz to show final score
    quiz_score = session.get('quiz_score', 0)
    q_index = session.get('q_index', 0)
    error_message = "The server encountered an error. Please select an option to continue."
    return(render_template('quiz_end.html', correct=quiz_score, total_qs=q_index, error=error_message, percent=get_percentage(quiz_score, q_index)))


# This route takes the user to the study section of the website
@app.route('/study')
def study():
    # initialize quiz variables in sessions
    session['quiz_score'] = 0
    session['q_index'] = 0

    # store the question IDs in a list to access database questions later
    question_ids = []
    query = client.query(kind=constants.questions)
    results = list(query.fetch())
    for e in results:
        question_ids.append(e.key.id)
        
    # shuffle question ids each time quiz is played
    random.shuffle(question_ids)
    
    # store the ids of the randomized quiz in a session object
    session['questions'] = question_ids

    # sleeping may help reduce number of internal server errors
    time.sleep(1)
    return render_template('study.html')


# This route takes the user to the quiz questions
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Use GET method to show question
    if request.method == 'GET':
        quiz_score = session.get('quiz_score', 0)
        q_index = session.get('q_index', 0)
        questions_ids = session.get('questions')
        time.sleep(1)

        # Increment question index (incrementing here ensures result page matches question asked)
        q_index += 1
        session['q_index'] = q_index

        # Show next question (-1 to account for indexing starting at 0)
        q_key = client.key(constants.questions, int(questions_ids[q_index-1]))
        question = client.get(key=q_key)
        return(render_template('quiz.html', question = question))    

    # Use POST method to show result
    if request.method == 'POST':
        quiz_score = session.get('quiz_score', 0)
        q_index = session.get('q_index', 0)
        questions_ids = session.get('questions', 0) 
        time.sleep(1)

        # end var controls which button to show on results page (if quiz is over)
        end = False
        if q_index == len(questions_ids):
            end = True
    
        q_key = client.key(constants.questions, int(questions_ids[q_index-1]))
        question = client.get(key=q_key)

        # Increment user's score if answer is correct (based on first char of form selection)
        user_ans = request.form.get('options')[0]
        result = "incorrect"
        if user_ans == question["answer"]:
            result = "correct!"
            quiz_score += 1
            session['quiz_score'] = quiz_score
        
        # Update T/F so that full word is printed on the results page
        if user_ans == "T":
            user_ans = "True"
        elif user_ans == "F":
            user_ans = "False"

        # Retrieve question information to pass to template
        return render_template('question_result.html', correct=quiz_score, qs_asked=q_index, total_qs=len(questions_ids),
                           percent = get_percentage(quiz_score, q_index), result=result, question=question, answer=user_ans, end=end)


# This route takes the user to the quiz final results page (if they choose to end quiz early or get an internal error)
@app.route('/quiz_end', methods=['GET'])
def quiz_end():
    quiz_score = session.get('quiz_score', 0)
    q_index = session.get('q_index', 0)
    return(render_template('quiz_end.html', correct=quiz_score, total_qs=q_index, error=False, percent=get_percentage(quiz_score, q_index)))


# This route takes the user to the game play landing page
@app.route('/play')
def play():
    # initialize game variables
    session['game_score'] = 0
    session['image_index'] = 0

    # shuffle images
    random.shuffle(game_images)

    # store the shuffled game images in a session object
    session['game'] = game_images
    return render_template('game.html')


# This route takes the user to the game play section
@app.route('/game', methods=['GET', 'POST'])
def play_game():
    # Access to session game variables
    image_index = session.get('image_index', 0)
    game_score = session.get('game_score', 0)
    game_images = session.get('game', 0)
    
    # Use GET method to show first image
    if request.method == "GET":
        image_url = game_images[image_index]["image"]
        hint = game_images[image_index]["hint"]
        return render_template('game_play.html', image=image_url, hint=hint, result=False)
        
    # Use POST method to show questions after 1st image (includes result text)
    if request.method == "POST":
        # Exit game after all images have been shown
        if image_index == len(game_images)-1:
            return render_template('game_results.html')

        else:
            result = "incorrect – try again"
            # Increment score and image_index if answer is correct
            user_answer = request.form["category"]
            if user_answer in game_images[image_index]["answer"]:
                result = "Correct!"

                # Show alternative answer for images that have more than 1 category
                if len(game_images[image_index]["answer"]) > 1:
                    answers = game_images[image_index]["answer"]
                    answers.remove(user_answer)
                    result = f"Correct! (Another correct category is {answers[0]})"
                
                image_index += 1   
                game_score += 1 
                session['image_index'] = image_index
                session['game_score'] = game_score

            # Show next image (or repeat image until user answers correctly)
            image_url = game_images[image_index]["image"]
            last_image = game_images[image_index-1]["image"]
            hint = game_images[image_index]["hint"]
            return render_template('game_play.html', 
                                   answer=user_answer.capitalize(), image=image_url, last=last_image, 
                                   hint=hint, result=result, score=game_score, questions=len(game_images))


# This route takes the user to the game review page to see questions & answers
@app.route('/review', methods=['GET', 'POST'])
def game_review():
    # Use GET method to show page for 1st time (question categories only)
    if request.method == "GET":
        return(render_template('game_review.html'))
    
    # Use POST method to show answers for the category question that user selects
    if request.method == "POST":
        category = request.form["category"]

        # Switch statement to display proper category question
        match category:
            case "question 1":
                question = "How do we know the globe is warming?"
            case "question 2":
                question = "How do we know greenhouse gases warm the air?"
            case "question 3":
                question = "How do we know the warming is not from the Sun?"
            case "question 4":
                question = "How do we know CO2 is not from volcanoes?"
            case "question 5":
                question = "How do we know CO2 is from humans?"
            case "question 6":
                question = "How do we know climate change is not just natural variability?"
            case "question 7":
                question = "How do we know warming / climate change matters?"

        # append images for category choice to display on page
        images = []
        for image in game_images:
            if category in image['answer']:
                images.append(image)
        return(render_template('game_review.html', images=images, question=question))
    

# This route takes the user to the admin login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        password = request.form['password']
        if password != 'jilliani$great':
            return redirect(url_for('login'))
        session['admin'] = True
        return redirect(url_for('admin'))


# This route takes the user to the admin homepage
@app.route('/admin')
def admin():
    if session.get('admin') == False:
        return redirect(url_for('login'))
    query = client.query(kind=constants.questions)
    results = list(query.fetch())
    q_list = []
    for e in results:
        q_list.append(str(e["question"]))
    return render_template('admin.html',q_list=q_list)


# Admin routes for adding a question
@app.route('/addq')
def add_page():
    return render_template('addq.html')

@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        content = request.form
        #parsing the form to format the data properly
        question = content['question']
        question.capitalize()
        #choices string parsing
        choices_str = str(content['choices'])
        choices = choices_str.split(';')
        #answer parsing
        answer = content['answer']
        answer.capitalize()
        #week parsing
        week = content['week']
        #Image string parsing
        img_str = str(content['image'])
        images = img_str.split(';')
        # adding question to database based on parsed data
        new_q = datastore.entity.Entity(key=client.key(constants.questions))
        new_q.update({"question": question, "choices": choices,
          "answer": answer, "week": week, "image": images} )
        client.put(new_q)
        return redirect(url_for('admin'))


# Admin routes for editing a question
@app.route('/editq')
def edit_page():
    query = client.query(kind=constants.questions)
    results = list(query.fetch())
    q_list = []
    for e in results:
        q_list.append(str(e["question"]))
    if len(q_list) == 0:
        return redirect(url_for('admin'))
    
    # Sory list to display questions alphabetically
    q_list.sort()
    return render_template('editq_choice.html', q_list=q_list)

@app.route('/edit_choice', methods=["POST"])
def edit_question():
    content= request.form['question_to_edit']
    if request.method == 'POST':
        query = client.query(kind=constants.questions)
        results = list(query.fetch())
        for e in results:
            if str(e["question"]) == str(content):
                q_key = client.key(constants.questions, int(e.key.id))
                question_obj = client.get(key=q_key)
                answer = question_obj['answer']
                choices = ';'.join(question_obj['choices'])
                image = ';'.join(question_obj['image'])
                id = str(e.key.id)
                question = question_obj['question']
                week = question_obj['week']
                return render_template('editq_question.html', answer=answer, 
                                       choices=choices,image=image,question=question,week=week,id=id)
            
@app.route('/edit', methods=['POST'])
def edit():
    if request.method == 'POST':
        content = request.form
        query = client.query(kind=constants.questions)
        results = list(query.fetch())
        db_question = request.form['id']
        for e in results:
            if str(e.key.id) == str(db_question):
                q_key = client.key(constants.questions, int(e.key.id))
                q_to_edit = client.get(key=q_key)
        
        #parsing the form to format the data properly
        question = content['question']
        question.capitalize()
        #choices string parsing
        choices_str = str(content['choices'])
        choices = choices_str.split(';')
        #answer parsing
        answer = content['answer']
        answer.capitalize()
        #week parsing
        week = content['week']
        #Image string parsing
        img_str = str(content['image'])
        images = img_str.split(';')

        # adding question to database based on parsed data

        q_to_edit.update({"question": question, "choices": choices,
          "answer": answer, "week": week, "image": images} )
        client.put(q_to_edit)
    return redirect(url_for('admin'))


# Admin routes for deleting a question
@app.route('/deleteq')
def delete_page():
    query = client.query(kind=constants.questions)
    results = list(query.fetch())
    q_list = []
    for e in results:
        q_list.append(str(e["question"]))
    if len(q_list) == 0:
        return redirect(url_for('admin'))
    
    # Sory list to display questions alphabetically
    q_list.sort()
    return render_template('deleteq.html', q_list=q_list)

@app.route('/delete', methods=["POST"])
def delete():
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


# Helper function to determine user's current quiz percentage
def get_percentage(score, index):
    if index != 0:
        percent = score / (index) * 100
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
    