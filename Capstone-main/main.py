from flask import Flask, render_template, request, session, redirect, url_for
from questions import questions
import random
from google.cloud import datastore
import constants
from game_images import game_images

app = Flask(__name__)
client = datastore.Client()


#Global variables for quiz study
quiz_score = 0
q_index = 0

#Global variables for game play
image_index = 0
game_score = 0


# This route takes the user to the homepage
@app.route('/')
def index():
    return render_template('index.html')


# This route takes the user to the study section of the website
@app.route('/study')
def study():
    # reset score and question index to 0
    global quiz_score
    global q_index
    quiz_score = 0
    q_index = 0

    # shuffle questions each time quiz is being played
    random.shuffle(questions)

    return render_template('study.html')


# This route takes the user to the quiz questions
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Access to global quiz variables
    global quiz_score
    global q_index

    # Use GET method to show question
    if request.method == 'GET':    
        # Increment question index (incrementing here ensures result page matches question asked)
        q_index += 1

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
        
        # Update T/F so that full word is printed on the results page
        if user_ans == "T":
            user_ans = "True"
        elif user_ans == "F":
            user_ans = "False"

        # Retrieve question information to pass to template
        question = questions[q_index-1]
        return render_template('question_result.html', correct = quiz_score, qs_asked = q_index, total_qs = len(questions),
                           percent = get_percentage(), result = result, question = question, answer = user_ans, end = end)


# This route takes the user to the quiz final results page (if they choose to end quiz early)
@app.route('/quiz_end', methods=['GET'])
def quiz_end():
    return(render_template('quiz_end.html', correct = quiz_score, total_qs = q_index, percent = get_percentage()))


# This route takes the user to the game page 
@app.route('/play')
def play():

    # reset score and image index to 0
    global image_index
    global game_score
    image_index = 0
    game_score = 0

    # shuffle images
    random.shuffle(game_images)
    return render_template('game.html')

@app.route('/game', methods=["GET", "POST"])
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


# Helper function to determine user's current quiz percentage
def get_percentage():
    if q_index != 0:
        percent = quiz_score / (q_index) * 100
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
    