"""
Docs:
https://pythonrepo.com/repo/twilio-twilio-python--python-third-party-apis-wrappers

https://www.twilio.com/docs/messaging/twiml
https://www.twilio.com/docs/usage/webhooks/sms-webhooks

https://docs.replit.com/tutorials/11-using-the-replit-database
https://docs.replit.com/misc/database
"""

from logging import debug
import uuid
from flask import Flask, request, jsonify
from flask.json import jsonify

import json

from replit import db as DB

from decouple import config

from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from twilio.rest import Client

import shortuuid

from multiprocessing.dummy import Pool

import requests

app = Flask("telefono_roto")

DEBUG_MODE = config("DEBUG_ENABLED", False)

ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", cast=str)
ACCOUNT_TOKEN = config("TWILIO_AUTH_TOKEN", cast=str)

TwilioClient = Client(ACCOUNT_SID, ACCOUNT_TOKEN)

APP_PHONE_ORIGIN = config("APP_PHONE_ORIGIN", cast=str)
TwilioClient.from_ = APP_PHONE_ORIGIN

TONGUE_TWISTER = "She sells seashells by the seashore"

APP_URL = config(
    "APP_URL", "https://app-bootcamp-paurulan-telefonoroto.twiliobootcamp.repl.co/"
)
CALL_URL = f"{APP_URL}/call"
CALL_WITH_RECORDING_CALLBACK_URL = f"{APP_URL}/call/callback"


class Player:
    def __init__(self, phone_number, uuid=None):
        self.phone_number = phone_number
        #
        self.uuid = uuid
        if not self.uuid:
            self.uuid = shortuuid.uuid()

    def __str__(self):
        return self.uuid

    def store(self):
        DB[f"user:{self.uuid}"] = self.phone_number

    def enqueue(self):
        DB[f"queue:{self.uuid}"] = self.uuid

    def unqueue(self):
        k = f"queue:{self.uuid}"
        if k in DB:
            DB.pop(k)

    def conference_queue(self):
        DB[f"conference:{self.uuid}"] = self.uuid

    def remove(self):
        """
        Remove the user from the database and notify them they are out the system.
        """
        k = f"user:{self.uuid}"
        if k in DB:
            DB.pop(k)

    def call_with_recording(self, recording_url):
        # Start our TwiML response
        response = VoiceResponse()

        response.play("", "w" * 2)
        response.say("Ahoy! This is a call from the TelefonoRoto game.")
        response.say(
            "First, we will play a recording of the last sentence and later you will have to repeat the message"
        )
        response.say("The message is:")

        if recording_url:
            response.play(recording_url)
        else:
            # default saying in case of first user
            response.say(TONGUE_TWISTER)

        response.say("Now please record your answer")
        # Use <Record> to record the caller's message
        response.record(
            play_beep=True,
            trim=True,
            recording_status_callback=CALL_WITH_RECORDING_CALLBACK_URL,
        )
        # End the call with <Hangup>
        response.hangup()

        call_twiml = str(response)
        print(call_twiml)

        call = TwilioClient.calls.create(
            to=self.phone_number,
            from_=TwilioClient.from_,
            twiml=call_twiml,
        )

        DB[f"call_sid:{call.sid}"] = self.uuid

        return call.sid

    def ending_call(self, recording_url):
        response = VoiceResponse()
        response.play("", "w" * 2)
        response.say("Ahoy! This round of TelefonoRoto has finished")
        response.say("The initial message was")
        response.say(TONGUE_TWISTER)

        response.say("The last message is:")
        response.play(recording_url)

        response.say("Thank you for playing ")
        response.say("We hope at least you laughted a little ")
        response.say(
            "Your phone number will now be removed for privacy, so do not worry about anything"
        )
        response.hangup()

        call_twiml = str(response)

        call = TwilioClient.calls.create(
            to=self.phone_number,
            from_=TwilioClient.from_,
            twiml=call_twiml,
        )

        return call.sid

    @classmethod
    def retrieve_player(cls, uuid):
        phone_number = DB.get(f"user:{uuid}")
        player = Player(phone_number, uuid=uuid)
        return player

    @classmethod
    def next_player(cls):
        queued_users = DB.prefix("queue:")
        if not queued_users:
            return
        uuid = DB[queued_users[0]]
        return Player.retrieve_player(uuid=uuid)


@app.route("/call", methods=["GET", "POST"])
def call_user():
    player = Player.next_player()
    if not player:
        return jsonify({"message": "no users found"})

    recording_url = DB.get("recording:last_url")
    player.call_with_recording(recording_url=recording_url)
    response = {
        "player": str(player),
        "message": "calling",
        "recording_url": recording_url,
    }
    return jsonify(response)


@app.route("/end", methods=["GET"])
def end_game():
    players_ids = DB.prefix("conference:")
    if not players_ids:
        return jsonify({"message": "no players found"})

    recording_url = DB.get("recording:last_url")
    response = {
        "n_player": len(players_ids),
        "recording_url": recording_url,
    }

    for conference_id in players_ids:
        uuid = DB.pop(conference_id)
        player = Player.retrieve_player(uuid)
        player.remove()
        player.ending_call(recording_url)

    return jsonify(response)


@app.route("/call/callback", methods=["GET", "POST"])
def call_user_callback():
    """
    https://www.twilio.com/docs/voice/api/call-resource#recordingstatuscallback
    """

    call_sid = request.args["CallSid"]
    recording_url = request.args["RecordingUrl"]

    call_user_uuid = DB.pop(f"call_sid:{call_sid}")
    player = Player.retrieve_player(uuid=call_user_uuid)
    player.conference_queue()
    player.unqueue()

    # update the recording pointer
    DB["recording:last_url"] = recording_url

    conference_count = len(DB.prefix("conference:"))
    if not Player.next_player() and conference_count >= 5:
        NEXT_ACTION = "/call/end_conference"
    else:
        NEXT_ACTION = "/call"

    Pool().apply_async(
        requests.get,
        [NEXT_ACTION],
    )
    return jsonify({"success": "ok"})


@app.route("/sms/register", methods=["POST"])
def register_from_sms():
    _s = (
        "You have been registered for the next round of TelefonoRoto. "
        "To keep your privacy, your phone number will be removed from the system after playing a single round. "
    )
    response = MessagingResponse()
    response.message(_s)
    #
    phone_number = request.form.get("From")
    player = Player(phone_number=phone_number)
    player.store()
    player.enqueue()
    # launch the start signal
    Pool().apply_async(
        requests.get,
        [CALL_URL],
    )
    #
    return str(response)


def delete_from_system():
    for player in round_players:
        player.remove()


@app.route("/", methods=["GET", "POST"])
def index():
    _s = "Text for index"
    response = MessagingResponse()
    response.message(_s)
    return str(response)


@app.route("/database", methods=["GET"])
def debug_database():
    data = {k: v for k, v in DB.items()}
    for k, v in data.items():
        if k.startswith("user:"):
            data[k] = "SECRET__" + v[-2:]
    return jsonify(data)


@app.route("/database/users", methods=["GET"])
def list_users_in_database():
    debug_data = dict()
    debug_data.update({k: DB.get(k) for k in DB.prefix("user:")})
    return jsonify(debug_data)


@app.route("/database/clear", methods=["GET"])
def clear_database():
    DB.clear()
    return jsonify({"success": True})


@app.route("/debug", methods=["POST"])
def webhook_debug():
    return ""


app.run(debug=DEBUG_MODE, host="0.0.0.0", port=8080)
