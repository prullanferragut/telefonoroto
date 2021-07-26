
"""
Docs:
https://pythonrepo.com/repo/twilio-twilio-python--python-third-party-apis-wrappers

https://www.twilio.com/docs/messaging/twiml

https://docs.replit.com/tutorials/11-using-the-replit-database
https://docs.replit.com/misc/database
"""

from flask import Flask

from replit import db as DB

from decouple import config

from twilio.twiml.messaging_response import MessagingResponse

import shortuuid

app = Flask('bootcamp')

ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", cast=str)
ACCOUNT_TOKEN = config("TWILIO_AUTH_TOKEN", cast=str)

STAT_LIST = [
  "stats_sms_calls",
  "stats_current_registered",
  "stats_total_registered",
]

DB['waiting_keys'] = []

TongueTwister = "She sells seashells by the seashore"

class Player:

  def __init__(self, phone_number):
    self.uuid = shortuuid.uuid()
    self.phone_number = phone_number

  def store(self):
    DB[uid] = self.phone_number

  def enqueue(self):
    k = f"user_{self.uuid}"
    DB[k] = self.phone_number

  def remove():
    DB.delete(self.uuid)
    target = self.phone
  #
    DB['sms_calls'] += 1
    _s = ("You have been removed from the TelefonoRoto database. "
          "Please register again if you want to play another round!")
    response = MessagingResponse()
    response.message(_s)
    return str(response)

  def call_with_recording(self, recording_url):
    pass

  def call_to_start_round(self):
    make_say_tongue_twister
    pass

  def conference_for_results(self):
    url_starting
    url_ending
    s = "The round has finished"
    s2 = "The initial message was"
    s3 = "and the ending message was"
    s4 = "Thank you for playing"
    s5 = "Your phone number will now be removed for privacy, so do not worry about anything"

@app.route('/stats', methods=['GET'])
def stats():
  _stats = [f"{stat}: {DB.get(stat, 0)}" for stat in STAT_LIST]
  _stats = [DB.list("stats_")]
  return "\n".join(_stats)

@app.route('/sms/hello', methods=['GET', 'POST'])
def sms():
  DB['sms_calls'] += 1
  _s = "Hello from Bootcamp!"
  response = MessagingResponse()
  response.message(_s)
  return str(response)

@app.route('/sms/register', methods=['POST'])
def register_from_sms():
  origin = retrieve_phone_number_from_sms
  #
  DB['sms_calls'] += 1
  _s = ("You have been registered for the next round of TelefonoRoto. "
        "To keep your privacy, your phone number will be removed from the system after playing a single round. ")
  response = MessagingResponse()
  response.message(_s)
  return str(response)

def delete_from_system():
  for player in round_players:
    player.remove

@app.route('/', methods=['GET', 'POST'])
def index():
  _s = "Text for index"
  response = MessagingResponse()
  response.message(_s)
  return str(response)


app.run(debug=True, host='0.0.0.0', port=8080)
