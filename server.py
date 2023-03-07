import os
import sys

from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS, cross_origin

# application factory. We will create all of the interfaces here
def create_app():

    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # main route. This is essentially equivalent to the index.html file
    @app.route("/", methods=["GET", "POST"])
    @cross_origin()
    def index():

        # main webpage requested via typical web browser
        if request.method == "GET":
            return "<h1>The server is working! 🎉</h1>"

        # data sent to the server from the frontend via post method. Let's process it!
        elif request.method == "POST":
            
            # try to get the JSON request data
            try:
                data = request.get_json()
            except:
                return "Error: No JSON body was able to be decoded by the client!", 400

            # ~~~ Future AI function call here ~~~
            # ai_result = ai_function(data)
            ai_result = data  # temporary

            return jsonify(ai_result)  # send back the result to the frontend

        # neither get nor post
        else:
            return "Method not allowed", 405

    # This is a simple route to test if the server is working
    @app.route("/test", methods=["POST"])
    @cross_origin()
    def ask():
        print("Test recieved")
        try:
            data = request.get_json()
            print(data)
        except:
            pass
        return "Success!"

    return app

