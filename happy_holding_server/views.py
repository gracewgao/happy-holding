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
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.voice_response import VoiceResponse, Play

from settings import ACCOUNT_SID, AUTH_TOKEN
from twilio.rest import Client

from happy_holding_server import app
from happy_holding_server.view_helpers import twiml_resp

from .db import get_db


@app.route('/')
@app.route('/happy')
def home():
    return render_template('index.html')


@app.route('/happy/welcome', methods=['POST'])
def welcome():
    response = VoiceResponse()
    with response.gather(
            num_digits=1, action=url_for('menu'), method="POST"
    ) as g:
        g.say(message="Hello, thank you for calling,,," +
                      "While you wait to speak to a representative, consider playing our fintastic game! "
                      "Please press 1 to start the quiz,,," +
                      "or press 2 for for regular hold music,,,,,", loop=1)
    return twiml_resp(response)


@app.route('/happy/menu', methods=['POST'])
def menu():
    response = VoiceResponse()
    selected_option = request.form['Digits']
    option_actions = {'1': _start_questions,
                      '2': _play_music}

    if selected_option in option_actions:
        option_actions[selected_option](response)
        return twiml_resp(response)

    return twiml_resp(response)


@app.route('/happy/music', methods=['POST'])
def music():
    response = VoiceResponse()
    # bonnie's bops!
    url = "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/54470100-46cf-448c-b968-23b226eac638/music.mp3?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20201122%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20201122T100457Z&X-Amz-Expires=86400&X-Amz-Signature=984eafca1aef5b3c2687084a09c0db0a47037a39619a90c47dd04ce3bbc313f2&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22music.mp3%22";
    response.play(url, loop=10)
    response.redirect(url_for('agent'))

    return twiml_resp(response)


@app.route('/happy/agent', methods=['POST'])
def agent():
    response = VoiceResponse()
    response.say(
        "Thanks for your patience!, You'll be redirected to the next available agent"
    )
    agents = ["+16139810982"]
    available = agents[0]
    response.dial(available)
    return twiml_resp(response)


@app.route('/happy/gameover', methods=['POST'])
def gameover():
    correct = request.args.get('correct')
    total = request.args.get('total')

    message_body = 'Thanks for playing Fintastic Trivia! Your score was {} out of {}'.format(correct,
                                                                                             str(int(total) + 1))

    # the magic 'from' number used for testing
    twilio_number = "+15005550006"
    caller = "+16139810982"

    # twilio_number = request.values.get('To')
    # caller = request.values.get('From')

    _send_sms(caller, twilio_number, message_body)

    voice_resp = VoiceResponse()
    voice_resp.say(message_body)

    voice_resp.redirect(url_for('agent'))
    return twiml_resp(voice_resp)


@app.route('/happy/answer', methods=['POST'])
def answer():
    n = int(request.args.get('question'))
    i = int(request.args.get('repeat'))
    score = int(request.args.get('score'))

    db = get_db()

    question = db.execute(
        'SELECT correct, feedback FROM questions WHERE question_id=?', str(n)
    ).fetchone()

    correct = int(question[0])
    selected_option = request.form['Digits']

    response = VoiceResponse()

    if correct == int(selected_option):
        response.say("That's right!")
        score += 1
    else:
        response.say("So close!")

    # returns feedback
    response.say(question[1])
    # enters into database
    _insert_response(n, selected_option)

    # repeats more questions
    if i < 2:
        response.redirect(url_for('ask', repeat=i + 1, score=score))
    else:
        response.redirect(url_for('gameover', correct=score, total=i))

    return twiml_resp(response)


@app.route('/happy/ask', methods=['POST'])
def ask():
    i = int(request.args.get('repeat'))
    score = int(request.args.get('score'))

    response = VoiceResponse()
    db = get_db()
    questions = db.execute(
        'SELECT question FROM questions'
    ).fetchall()
    n = i
    # n = randrange(0, 4)
    q = questions[n]
    with response.gather(
            num_digits=1, action=url_for('answer', question=n, repeat=i, score=score), method="POST"
    ) as g:
        g.say("Question " + str(i + 1) + ",,")
        g.say(message=str(q[0])
                      + "Please enter your answer now using the number pad,,,,,,", loop=1)
    return twiml_resp(response)


# private methods

def _start_questions(response):
    response.redirect(url_for('ask', repeat=0, score=0))


def _insert_response(question, selected):
    db = get_db()
    db.execute(
        'INSERT INTO log'
        ' VALUES (?, ?)',
        (question, selected)
    )
    db.commit()


def _play_music(response):
    response.redirect(url_for('music'))


def _send_sms(to_number, from_number, message):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    try:
        client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
    except TwilioRestException as exception:
        # check for invalid mobile number error from Twilio
        if exception.code == 21614:
            print("Uh oh, looks like this caller can't receive SMS messages.")
