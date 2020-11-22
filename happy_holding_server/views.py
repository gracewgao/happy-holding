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
    option_actions = {'1': _start_questions,
                      '2': _play_music}

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


@app.route('/ivr/sms', methods=['POST'])
def sms():
    correct = request.args.get('correct')
    total = request.args.get('total')

    response = MessagingResponse()
    message_body = 'Thanks for playing Fintastic Trivia! You score was {} out of {}'.format(correct, total)
    response.message(message_body)

    voice_resp = VoiceResponse()
    voice_resp.say(message_body)

    response.redirect(url_for('agent'))
    return twiml_resp(response)


@app.route('/ivr/answer', methods=['POST'])
def answer():
    n = int(request.args.get('question'))
    i = int(request.args.get('repeat'))
    score = int(request.args.get('score'))

    db = get_db()

    question = db.execute(
        'SELECT answer, feedback FROM testquestions2 WHERE question_id=?', str(n)
    ).fetchone()

    correct = int(question[0])
    selected_option = request.form['Digits']

    response = VoiceResponse()

    if correct == int(selected_option):
        response.say("That's right!")
        score += 1
    else:
        response.say("So close!, The correct answer was " + str(correct))

    # returns feedback
    response.say(question[1])
    # enters into database
    _insert_response(n, selected_option)

    # repeats more questions
    if i < 2:
        response.redirect(url_for('ask', repeat=i + 1, score=score))
    else:
        response.redirect(url_for('sms', correct=score, total=i))

    return twiml_resp(response)


@app.route('/ivr/ask', methods=['POST'])
def ask():
    i = int(request.args.get('repeat'))
    score = int(request.args.get('score'))

    response = VoiceResponse()
    db = get_db()
    questions = db.execute(
        'SELECT question, answer FROM testquestions2'
    ).fetchall()
    n = 0
    # n = randrange(0, 0)
    q = questions[n]
    with response.gather(
            num_digits=1, action=url_for('answer', question=n, repeat=i, score=score), method="POST"
    ) as g:
        g.say("Question " + str(i + 1) + ",,")
        g.say(message=str(q[0])
                      + "Please enter your answer now using the number pad,,,", loop=3)
    return twiml_resp(response)


# private methods

def _start_questions(response):
    response.redirect(url_for('ask', repeat=0, score=0))


def _insert_response(question, selected):
    db = get_db()
    db.execute(
        'INSERT INTO testing'
        ' VALUES (?, ?)',
        (question, selected)
    )
    db.commit()


def _play_music(response):
    pass


def _redirect_welcome():
    response = VoiceResponse()
    response.say("Returning to the main menu", voice="alice", language="en-GB")
    response.redirect(url_for('welcome'))

    return twiml_resp(response)
