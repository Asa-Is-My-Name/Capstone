from flask import Flask, render_template, request, session, redirect, url_for
import random
from google.cloud import datastore
import constants
from questions import questions
from game_images import game_images
import os

os.environ["GCLOUD_PROJECT"] = "capstone-384605"

app = Flask(__name__)
client = datastore.Client()

# set a secret key (to use for sessions)
app.secret_key = os.urandom(24)


# This route takes the user to the homepage
@app.route('/')
def index():
    return render_template('index.html')


# This route takes the user to the study section of the website
@app.route('/study')
def study():
    # initialize quiz variables
    session['quiz_score'] = 0
    session['q_index'] = 0

    # shuffle questions each time quiz is being played
    random.shuffle(questions)
    return render_template('study.html')


# This route takes the user to the quiz questions
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Access to session quiz variables
    quiz_score = session.get('quiz_score', 0)
    q_index = session.get('q_index', 0)

    # Use GET method to show question
    if request.method == 'GET':    
        # Increment question index (incrementing here ensures result page matches question asked)
        q_index += 1
        session['q_index'] = q_index

        # Show next question (-1 to account for indexing starting at 0)
        question = questions[q_index-1]
        return(render_template('quiz.html', question = question))
        

    # Use POST method to show result
    if request.method == 'POST': 
        # end var controls which button to show on results page (if quiz is over)
        end = False
        if q_index == len(questions):
            end = True

        # Increment user's score if answer is correct (based on first char of form selection)
        user_ans = request.form.get('options')[0]
        result = "incorrect"
        if user_ans == questions[q_index-1]["answer"]:
            result = "correct!"
            quiz_score += 1
            session['quiz_score'] = quiz_score
        
        # Update T/F so that full word is printed on the results page
        if user_ans == "T":
            user_ans = "True"
        elif user_ans == "F":
            user_ans = "False"

        # Retrieve question information to pass to template
        question = questions[q_index-1]
        return render_template('question_result.html', correct=quiz_score, qs_asked=q_index, total_qs=len(questions),
                           percent = get_percentage(quiz_score, q_index), result=result, question=question, answer=user_ans, end=end)


# This route takes the user to the quiz final results page (if they choose to end quiz early)
@app.route('/quiz_end', methods=['GET'])
def quiz_end():
    quiz_score = session.get('quiz_score', 0)
    q_index = session.get('q_index', 0)
    return(render_template('quiz_end.html', correct=quiz_score, total_qs=q_index, percent=get_percentage(quiz_score, q_index)))


# This route takes the user to the game review page to see questions & answers
@app.route('/review', methods=['GET', 'POST'])
def game_review():
    # Use GET method to show page for the 1st time (question categories only)
    if request.method == "GET":
        return(render_template('game_review.html'))
    
    # Use POST method to show answers for the category question that user selects
    if request.method == "POST":
        category = request.form["category"]

        # Switch statement to display proper category question
        match category:
            case "question 1":
                question = "How do we know if the globe is warming?"
            case "question 2":
                question = "How do we know greenhouse gases warm air?"
            case "question 3":
                question = "How do we know the warming is not from the sun?"
            case "question 4":
                question = "How do we know the CO2 is not from volcanoes?"
            case "question 5":
                question = "How do we know CO2 is from humans?"
            case "question 6":
                question = "Is climage change just natural variability?"
            case "question 7":
                question = "Why does it matter if temperatures are changing?"

        # append images for category choice to display on page
        images = []
        for image in game_images:
            if category in image['answer']:
                images.append(image)
        return(render_template('game_review.html', images=images, question=question))


# This route takes the user to the game play page 
@app.route('/play')
def play():
    # initialize game variables
    session['game_score'] = 0
    session['image_index'] = 0

    # shuffle images
    random.shuffle(game_images)
    return render_template('game.html')


@app.route('/game', methods=['GET', 'POST'])
def play_game():
    # Access to session game variables
    image_index = session.get('image_index', 0)
    game_score = session.get('game_score', 0)
    
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
                result = "correct!"
                # Show alternative answer for images that have more than 1 category
                if len(game_images[image_index]["answer"]) > 1:
                    answers = game_images[image_index]["answer"]
                    answers.remove(user_answer)
                    result = f"correct! Another correct category is {answers[0]}"
                image_index += 1   
                game_score += 1 
                session['image_index'] = image_index
                session['game_score'] = game_score

            # Show next image (or repeat image until user answers correctly)
            image_url = game_images[image_index]["image"]
            last_image = game_images[image_index-1]["image"]
            hint = game_images[image_index]["hint"]
            return render_template('game_play.html', answer=user_answer.capitalize(), image=image_url, last=last_image, hint=hint, result=result, score=game_score, questions=len(game_images))
    

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
    