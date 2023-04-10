import os
import sys
import numpy as np
from math import atan2

from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS, cross_origin

# global parameters
width = 540
height = 360
keyPoints = [0, 1, 4, 5, 9, 13, 17, 8, 12, 16, 20]
allPoints = list(range(0, 21))
thumbPoints = [0, 1, 2, 3, 4]
tol = 1500

# basically, some gestures were a lot harder to pass than others. This allows variability in acceptance prob
# fingers tolerance
tolerances_world = {'a': 0.6, 'b': 0.55, 'c': 0.8, 'd': 0.40, 'e': 0.5, 'f': 0.55, 'g': 0.8, 'h': 0.92, 'i': 0.75, 'k': 0.6, 'l': 0.5,
                    'm': 0.6, 'n': 0.6, 'o': 0.5, 'p': 1.5, 'q': 1, 'r': 0.5, 's': 0.5, 't': 0.85, 'u': 0.85, 'v': 0.95, 'w': 0.75, 'x': 0.5, 'y': 0.9}
tolerances_world_fingers = {"a": [0.08, 0.1, 0.1, 0.1, 0.1], "b": [
    0.17, 0.1, 0.1, 0.1, 0.1], "f": [0.1, 0.1, 0.1, 0.1, 0.1]}

# to avoid a poor user experience for the test day, add a tolerance for every gesture
for gesture, tolerance in tolerances_world.items():
    tolerances_world[gesture] = tolerance + 0.1

# stored gestures path
current_dir = os.path.dirname(os.path.realpath('__file__'))
rel_path = "gesturedatas" + os.sep + "gesture_info_alphabet_number_righthand.txt"
abs_file_path = os.path.join(current_dir, rel_path)
rel_path_world = "gesturedatas_world_coordinates" + \
    os.sep + "gesture_info_alphabet_number_righthand.txt"
abs_file_path_world = os.path.join(current_dir, rel_path_world)


# from raw data to handdata format
def jsonTohanddata(jsonData):
    name = jsonData["gesture"]
    if name.isalpha():
        gestureName = name.lower()
    elif name.isnumeric():
        gestureName = name
    else:
        print("unexpected gesture name")
        gestureName = None
    Handdata = []
    # go through landmarks in the first hand
    for landmark in jsonData["multiHandLandmarks"][0]:
        Handdata.append((int(landmark["x"]*width), int(landmark["y"]*height)))

    Handdata_world = []
    # go through landmarks, but save the world coordinate data
    for landmark in jsonData["multiHandWorldLandmarks"][0]:
        Handdata_world.append(
            (float(landmark["x"]), float(landmark["y"]), float(landmark["z"])))
        pass

    return gestureName, Handdata, Handdata_world

# read stored gesture info from file


def readGestInfo(filepath):
    gesture_dict = {}
    gesture_data = []
    start_flag = 1
    with open(filepath, 'r') as fp_read:
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

            pos_tuple = tuple(map(float, pos.split(' ')))
            gesture_data.append(pos_tuple)

        else:
            gesture_dict[gesture_name_temp] = gesture_data
    return gesture_dict


GESTURES_DICT = readGestInfo(abs_file_path)
GESTURES_DICT_WORLD = readGestInfo(abs_file_path_world)

# Euclidean distance matrix functions


def getDistancesMatrix(handData):
    numjoints = len(handData)
    distMatrix = np.zeros([numjoints, numjoints], dtype='float')
    handData_array = np.array(handData)
    handmatrix = np.repeat(handData_array[np.newaxis, :, :], numjoints, axis=0)
    handmatrixT = np.transpose(handmatrix, (1, 0, 2))
    distMatrix = np.linalg.norm(handmatrix - handmatrixT, axis=2)

    return distMatrix


def getFingerdata(handData, fingerPoints):
    fingerdata = [handData[i] for i in fingerPoints]
    return fingerdata


def getAbsoluteAngle(point1, point2, fixedpoint):
    point1_ar = np.asarray(point1)
    point2_ar = np.asarray(point2)
    fixedpoint_ar = np.asarray(fixedpoint)
    line1 = point1_ar - fixedpoint_ar
    line2 = point2_ar - fixedpoint_ar

    cosine_angle = np.dot(line1, line2) / \
        (np.linalg.norm(line1) * np.linalg.norm(line2))
    angle = np.arccos(cosine_angle)
    return angle


def getJointsAngles(fingerdata):
    # calculate angles in terms of the fixed point(the joint angle we need)
    angle1 = getAbsoluteAngle(fingerdata[0], fingerdata[2], fingerdata[1])
    angle2 = getAbsoluteAngle(fingerdata[1], fingerdata[3], fingerdata[2])
    angle3 = getAbsoluteAngle(fingerdata[2], fingerdata[4], fingerdata[3])
    # print([angle1, angle2, angle3])
    return np.array([angle1, angle2, angle3])


def findError(gestureMatrix, unknownMatrix, keyPoints):
    error = 0
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

    response = {}
    accepted = error < tol
    # boolean not serializable? how silly!
    response["accepted"] = str(accepted)
    response["error"] = error
    response["tolerance"] = tol
    return response


def verifyGestureWorld(unknownGestureData, dictGesture, keyPoints, gestName):
    knownGestureData = dictGesture[gestName]
    # unknownGesture = np.matrix(unknownGestureData)
    # knownGesture = np.matrix(knownGestureData)

    unknownGestureDistMatrix = getDistancesMatrix(unknownGestureData)
    knownGestureDistMatrix = getDistancesMatrix(knownGestureData)
    total_error = findError(unknownGestureDistMatrix,
                            knownGestureDistMatrix, keyPoints)

    # calculate dist matrix for all landmarks in thumb
    # thumb_error = findError(unknownGestureDistMatrix,
    #                         knownGestureDistMatrix, thumbPoints)

    # calculate the anlges of joint of thumb
    # unknownFingerData = getFingerdata(unknownGestureData, thumbPoints)
    # knownFingerData = getFingerdata(knownGestureData, thumbPoints)
    # unknownFingerAngle = getJointsAngles(unknownFingerData)
    # knownFingerAngle = getJointsAngles(knownFingerData)
    # thumb_error_angle = np.max(np.abs(unknownFingerAngle - knownFingerAngle))
    # print(thumb_error_angle)

    # find euclidean distance between points in the hand (which are rows). Units are in meters.
    # gesture_distance_deltas = knownGesture - unknownGesture
    # gesture_distance_deltas_squared = np.square(gesture_distance_deltas)
    # sums = np.sum(gesture_distance_deltas_squared, axis=1)  # row-wise sum gives us delta from point-to-point
    # euclidean_distance = np.sqrt(sums)

    # total_error = np.sum(euclidean_distance)
    # average_error = np.sum(euclidean_distance)

    tolerance = tolerances_world[gestName]
    # tolerance_fingers = tolerances_world_fingers[gestName][0]

    response = {}
    accepted = total_error < tolerance
    # boolean not serializable? how silly!
    response["accepted"] = str(accepted)
    response["error"] = total_error
    # response["error_avg"] = average_error
    response["tolerance"] = tolerance

    return response


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

            # if it was a test message, return a success message
            if data.get("test"):
                return jsonify("Success! 🎉")

            # ~~~ Future AI function call here ~~~
            # ai_result = ai_function(data)
            correctGestName, unknownhanddata, unknownhanddata_world = jsonTohanddata(
                data)
            # ai_result = verifyGesture(
            #     unknownhanddata, GESTURES_DICT, keyPoints, correctGestName, tol)
            ai_result_world = verifyGestureWorld(
                unknownhanddata_world, GESTURES_DICT_WORLD, keyPoints, correctGestName)

            # send back the result to the frontend
            return jsonify(ai_result_world)

        # neither get nor post
        else:
            return "Method not allowed", 405
        

    @app.route("/hand", methods=["GET"])
    @cross_origin()
    def hand_request():

        # try to get the JSON request data
        try:
            data = request.get_json()

        except:
            return jsonify("Error: No JSON body was able to be decoded by the client!"), 400

        # if it was a test message, return a success message
        if data.get("test"):
            return jsonify("Success! 🎉")

        # ~~~ Future AI function call here ~~~
        # ai_result = ai_function(data)
        correctGestName, unknownhanddata, unknownhanddata_world = jsonTohanddata(
            data)
        # ai_result = verifyGesture(
        #     unknownhanddata, GESTURES_DICT, keyPoints, correctGestName, tol)
        ai_result_world = verifyGestureWorld(
            unknownhanddata_world, GESTURES_DICT_WORLD, keyPoints, correctGestName)

        # send back the result to the frontend
        return jsonify(ai_result_world)

    return app

    

# def jsonTohanddata(jsonData)
#     HandData = [ ]
#     for landmark in jsonData["multiHandLandmarks"][0]:
#         x = landmark["x"]
#         y = landmark["y"]
#         z = landmark["z"]
#         HandData.append((int(x*width),int(y*height))
#     return gestureName, HandData
