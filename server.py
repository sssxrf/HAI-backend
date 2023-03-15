import os
import sys
import numpy as np

from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS, cross_origin

# global parameters
width = 540
height = 360
keyPoints = [0,1,4,5,9,13,17,8,12,16,20]
allPoints = list(range(0, 21))
tol = 1500

# stored gestures path
current_dir = os.path.dirname(os.path.realpath('__file__'))
rel_path = "gesturedatas" + os.sep + "gesture_info_abcd.txt"
abs_file_path = os.path.join(current_dir, rel_path)


# from raw data to handdata format
def jsonTohanddata(jsonData):
    gestureName = 'a'
    Handdata = []
    # go through landmarks in the first hand
    for landmark in jsonData["multiHandLandmarks"][0]:
        Handdata.append((int(landmark["x"]*width),int(landmark["y"]*height)))
    return gestureName, Handdata

# read stored gesture info from file
def readGestInfo():
    gesture_dict = {}
    gesture_data = []
    start_flag = 1
    with open(abs_file_path, 'r') as fp_read:
        for line in fp_read:
            pos = line[:-1]
            if len(pos) == 1:
                if start_flag:
                    gesture_name_temp = pos
                    start_flag = 0
                    continue
                gesture_dict[gesture_name_temp] = gesture_data
                gesture_name_temp = pos
                gesture_data = []
                continue
            
            pos_tuple = tuple(map(int, pos.split(' ')))
            gesture_data.append(pos_tuple)

        else:
            gesture_dict[gesture_name_temp] = gesture_data
    return gesture_dict
GESTURES_DICT = readGestInfo()

#Euclidean distance matrix functions
def getDistancesMatrix(handData):
    numjoints = len(handData)
    distMatrix = np.zeros([numjoints, numjoints],dtype='float')
    handData_array = np.array(handData)
    handmatrix = np.repeat(handData_array[np.newaxis, :, :], numjoints, axis=0)
    handmatrixT = np.transpose(handmatrix, (1, 0, 2))
    distMatrix = np.linalg.norm(handmatrix - handmatrixT, axis = 2)

    return distMatrix
 
def findError(gestureMatrix, unknownMatrix, keyPoints):
    error=0
    points = np.array(keyPoints)
    errorMatrix = np.absolute(gestureMatrix - unknownMatrix)
    indices = np.ix_(points, points)
    error = errorMatrix[indices].sum()
    return error

def verifyGesture(unknownGestureData, dictGesture, keyPoints, gestName, tol):
    unknownGesture = getDistancesMatrix(unknownGestureData)
    knownGestureData = dictGesture[gestName]
    knownGesture = getDistancesMatrix(knownGestureData)
    error = findError(unknownGesture, knownGesture, keyPoints)

    respose = {}
    accepted = error < tol
    respose["accepted"] = str(accepted)  # boolean not serializable? how silly!
    respose["error"] = error
    respose["tolerance"] = tol
    return respose


# application factory. We will create all of the interfaces here
def create_app():

    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    app.config['CORS_HEADERS'] = 'no-cors'

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
                return jsonify("Error: No JSON body was able to be decoded by the client!"), 400

            # ~~~ Future AI function call here ~~~
            # ai_result = ai_function(data)
            correctGestName, unknownhanddata = jsonTohanddata(data)
            
            ai_result = verifyGesture(unknownhanddata, GESTURES_DICT, keyPoints, correctGestName, tol)

            return jsonify(ai_result)  # send back the result to the frontend

        # neither get nor post
        else:
            return "Method not allowed", 405


    return app

# def jsonTohanddata(jsonData)
#     HandData = [ ]
#     for landmark in jsonData["multiHandLandmarks"][0]:
#         x = landmark["x"]
#         y = landmark["y"]
#         z = landmark["z"]
#         HandData.append((int(x*width),int(y*height))
#     return gestureName, HandData

