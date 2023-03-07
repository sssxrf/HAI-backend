import os
import sys

from flask import Flask, redirect, url_for, request, jsonify

# application factory. We will create all of the interfaces here
def create_app():

    # create and configure the app
    app = Flask(__name__)

    # main route. This is essentially equivalent to the index.html file
    @app.route("/", methods=["GET", "POST"])
    def index():

        # main webpage requested via typical web browser
        if request.method == "GET":
            return "<h1>The server is working! 🎉</h1>"

        # data sent to the server from the frontend via post method. Let's process it!
        elif request.method == "POST":
            data = request.get_json()
            print(data)  # hand data from the client will be printed here

            # ~~~ Future AI function call here ~~~
            # ai_result = ai_function(data)
            ai_result = "Some AI result"

            return ai_result  # send back the result to the frontend

        # neither get nor post
        else:
            return "Method not allowed", 405

    return app