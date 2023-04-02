import cv2
import mediapipe as mp
import numpy as np
import os

# images folder where each gesture image is located
images_folder = os.path.abspath("images")

# parameters:
width = 540
height = 360
start_point = (120, 40)
end_point = (420, 320)
keyPoints = [0, 1, 4, 5, 9, 13, 17, 8, 12, 16, 20]
allPoints = list(range(0, 21))

# mp initial
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


# Euclidean distance matrix functions
def getDistancesMatrix(handData):
  numjoints = len(handData)
  distMatrix = np.zeros([numjoints, numjoints], dtype='float')
  handData_array = np.array(handData)
  handmatrix = np.repeat(handData_array[np.newaxis, :, :], numjoints, axis=0)
  handmatrixT = np.transpose(handmatrix, (1, 0, 2))
  distMatrix = np.linalg.norm(handmatrix - handmatrixT, axis=2)

  return distMatrix


def findError(gestureMatrix, unknownMatrix, keyPoints):
  error = 0
  points = np.array(keyPoints)
  errorMatrix = np.absolute(gestureMatrix - unknownMatrix)
  indices = np.ix_(points, points)
  error = errorMatrix[indices].sum()
  return error


def findGesture(unknownGesture, knownGestures, keyPoints, gestNames, tol):
  errorArray = []
  for i in range(0, len(gestNames)):
    error = findError(knownGestures[i], unknownGesture, keyPoints)
    errorArray.append(error)
  errorArray = np.array(errorArray)
  errorMin = np.min(errorArray)
  minIndex = np.argmin(errorArray)
  if errorMin < tol:
    gesture = gestNames[minIndex]
  if errorMin >= tol:
    gesture = 'Unknown'
  return gesture


# find the images and load each image path into a list
gesture_images = []
for file in os.listdir(images_folder):
  if file.endswith(".jpg"):
    gesture_name = file.split('.')[0]
    gesture_images.append((gesture_name, os.path.join(images_folder, file)))

# sort the list of images by gesture name
gesture_images = sorted(gesture_images, key=lambda x: x[0])

with mp_hands.Hands(
  model_complexity=0,
  min_detection_confidence=0.5,
  min_tracking_confidence=0.5) as hands:

  # save hand data for saving to a file later
  HandsWorldCoords = {}

  for gesture, gesture_image_path in gesture_images:
    # load the image
    image = cv2.flip(cv2.imread(gesture_image_path), 1)

    # show the loaded image
    # cv2.imshow('Gesture Image', image)
    # cv2.waitKey(0)

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # call mediapipe API to detect hands
    results = hands.process(image)

    # if there were no hands at all, alert the user, because this should never be the case
    if not results.multi_hand_landmarks:
      print(f"No hands detected in the image for {gesture}, please try again")
      break

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_world_landmarks:

      for hand_landmark_world in results.multi_hand_world_landmarks:
        # record the world coordinates of the hand
        HandWorld = []
        for landMark in hand_landmark_world.landmark:
          HandWorld.append((landMark.x, landMark.y, landMark.z))
        HandsWorldCoords[gesture] = HandWorld

        # make a copy of the image to mark up
        image_height, image_width, _ = image.shape
        annotated_image = image.copy()

        # draw the hand landmarks on the image
        for hand_landmarks in results.multi_hand_landmarks:
          mp_drawing.draw_landmarks(
            annotated_image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())

        # create a new image path for the annotated image
        annoted_images_folder = os.path.abspath("annotated_images")
        if not os.path.exists(annoted_images_folder):
          os.makedirs(annoted_images_folder)
        annotated_image_path = os.path.join(annoted_images_folder, f"{gesture}.jpg")

        # write the image
        cv2.imwrite(annotated_image_path, cv2.flip(annotated_image, 1))

  # store the hand data world coordinates in a file
  lines = []
  with open('gesturedatas_world_coordinates/gesture_info_alphabet_number_righthand.txt', 'w') as f:
    for gesture, world_coordinates in HandsWorldCoords.items():
      lines.append(f"{gesture}\n")
      for x, y, z in world_coordinates:
        lines.append(f"{x} {y} {z}\n")
    f.writelines(lines)
