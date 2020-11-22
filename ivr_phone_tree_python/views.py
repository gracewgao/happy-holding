import json

from flask import (
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for,
)
from twilio.twiml.voice_response import VoiceResponse

from ivr_phone_tree_python import app
from ivr_phone_tree_python.view_helpers import twiml

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
              "Please press 1 to begin." +
              "Press 2 for same calming music.", loop=3)
    return twiml(response)

@app.route('/ivr/menu', methods=['POST'])
def menu():

    selected_option = request.form['Digits']
    option_actions = {'1': _begin,
                      '2': _list_planets}

    if selected_option in option_actions:
        response = VoiceResponse()
        option_actions[selected_option](response)
        return twiml(response)

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
        return twiml(response)

    return _redirect_welcome()


# private methods

def _give_instructions(response):

    db = get_db()
    ratings = db.execute(
        'SELECT joint_id, AVG(rating) FROM ratings GROUP BY joint_id'
    ).fetchall()

    for r in ratings:
        response.say(str(r[0]))
        # ratings_json.append({'joint_id': r[0], 'rating': r[1]})

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

    return twiml(response)


