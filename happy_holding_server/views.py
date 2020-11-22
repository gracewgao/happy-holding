import json
from random import randrange

from flask import (
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for,
)
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import Message, MessagingResponse

from happy_holding_server import app
from happy_holding_server.view_helpers import twiml_resp

from .db import get_db

@app.route('/')
@app.route('/ivr')
def home():
    return render_template('index.html')


@app.route('/ivr/welcome', methods=['POST'])
def welcome():
    response = VoiceResponse()
    with response.gather(
        num_digits=1, action=url_for('menu'), method="POST"
    ) as g:
        g.say(message="Thank you for choosing to play this fintastic game." +
              "Please press 1 to begin,,," +
              "or press 2 for same calming music,,,", loop=3)
    return twiml_resp(response)

@app.route('/ivr/menu', methods=['POST'])
def menu():

    selected_option = request.form['Digits']
    option_actions = {'1': start_questions,
                      '2': _list_planets}

    if selected_option in option_actions:
        response = VoiceResponse()
        option_actions[selected_option](response)
        return twiml_resp(response)

    return _redirect_welcome()


@app.route('/ivr/planets', methods=['POST'])
def planets():
    selected_option = request.form['Digits']
    option_actions = {'2': "+12024173378",
                      '3': "+12027336386",
                      "4": "+12027336637"}

    if selected_option in option_actions:
        response = VoiceResponse()
        response.dial(option_actions[selected_option])
        return twiml_resp(response)

    return _redirect_welcome()

@app.route('/ivr/agent', methods=['POST'])
def agent():
    response = VoiceResponse()
    response.say(
        "Thanks for your patience!, You'll be redirected to the next available agent"
    )
    agents = ["+16139810982"]
    available = agents[0]
    response.dial(available)
    # forward_to_agent(response)
    return twiml_resp(response)

@app.route('/ivr/sms', methods=['GET', 'POST'])
def sms():
    correct = request.args.get('correct')
    total = request.args.get('total')
    response = MessagingResponse()
    message_body = 'Thanks for playing Fintastic Trivia! You score was {} out of {}'.format(correct, total)
    response.message(message_body)

    response.redirect(url_for('agent'))
    return twiml_resp(response)

@app.route('/ivr/answer', methods=['POST'])
def answer():
    db = get_db()
    n = request.args.get('question')
    question = db.execute(
        'SELECT answer, feedback FROM testquestions2 WHERE question_id=?', n
    ).fetchone()

    correct = int(question[0])
    selected_option = request.form['Digits']

    response = VoiceResponse()

    if correct == int(selected_option):
        response.say("That's right!")
    else:
        response.say("So close!, The correct answer was " + str(correct))

    response.say(question[1])

    insert_response(n, selected_option)
    response.redirect(url_for('sms', correct=8, total=10))

    return twiml_resp(response)


# private methods

def start_questions(response):
    db = get_db()
    questions = db.execute(
        'SELECT question, answer FROM testquestions2'
    ).fetchall()

    for i in range(3):
        n = 0
        # n = randrange(0, 0)
        q = questions[n]
        with response.gather(
            num_digits=1, action=url_for('answer', question=n), method="POST"
        ) as g:
            g.say("Question " + str(i + 1) + ",,")
            g.say(message=str(q[0])
                  + "Please enter your answer now using the number pad,,,", loop=3)

def forward_to_agent(response):
    response = VoiceResponse()

    agents = ["+16139810982"]
    available = agents[0]

    response.say(
        "Thanks for your patience!, You'll be redirected to the next available agent"
    )
    response.dial(
        available
    )

def insert_response(question, selected):
    db = get_db()
    db.execute(
        'INSERT INTO testing'
        ' VALUES (?, ?)',
        (question, selected)
    )
    db.commit()

def _give_instructions(response):

    db = get_db()
    ratings = db.execute(
        'SELECT joint_id, AVG(rating) FROM ratings GROUP BY joint_id'
    ).fetchall()

def _begin(response):
    with open('questions.json') as f:
        data = json.load(f)
        for p in data['questions']:
            response.say(p['question'] +
                         "Press 1 for " + p['answers'][0] +
                         "Press 2 for " + p['answers'][1] +
                         "Press 3 for " + p['answers'][2],
                         voice="alice", language="en-GB")

    response.hangup()
    return response


def _list_planets(response):
    with response.gather(
        numDigits=1, action=url_for('planets'), method="POST"
    ) as g:
        g.say("To call the planet Broh doe As O G, press 2. To call the " +
              "planet DuhGo bah, press 3. To call an oober asteroid " +
              "to your location, press 4. To go back to the main menu " +
              " press the star key.",
              voice="alice", language="en-GB", loop=3)

    return response


def _redirect_welcome():
    response = VoiceResponse()
    response.say("Returning to the main menu", voice="alice", language="en-GB")
    response.redirect(url_for('welcome'))

    return twiml_resp(response)


