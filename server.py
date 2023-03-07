import os
import sys

from flask import Flask, redirect, url_for, request, jsonify

def init_webhooks(base_url):
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():

        # main webpage requested
        if request.method == "GET":
            return "<h1>The server is working! 🎉</h1>"

        # data sent to the server from the frontend via post method. Let's process it!
        elif request.method == "POST":
            data = request.get_json()
            print(data)  # hand data from the client will be printed here

            return "OK"

        # neither get nor post
        else:
            return "Method not allowed", 405

    return app