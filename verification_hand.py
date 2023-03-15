import cv2
import mediapipe as mp
import numpy as np

# parameters:
width = 540
height = 360
start_point = (120, 40)
end_point = (420, 320)
keyPoints = [0,1,4,5,9,13,17,8,12,16,20]
allPoints = list(range(0, 21))

#mp initial
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# read prestore gesture matrix(stored in a dictionary)
gesture_dict = {}
gesture_data = []
start_flag = 1
with open(r'D:\\umich_course\\2023winter\\HCI-AI\\Final Project\\backend\\HAI-backend\\gesturedatas\\gesture_info_abcd.txt', 'r') as fp_read:
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
print('finish loading gesture data!')
print(gesture_dict)

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

def verifyGesture(unknownGesture, dictGesture, keyPoints, gestName, tol):
    knownGestureData = dictGesture[gestName]
    knownGesture = getDistancesMatrix(knownGestureData)
    error = findError(unknownGesture, knownGesture, keyPoints)
    if error < tol:
        gesture = gestName
    if error >= tol:
        gesture = 'wrong'
    return gesture


numGest = 1
 
gestNames = []
knownGestures = []
tol = 1500

for i in range(0, numGest, 1):
    prompt='Name of Gesture #'+str(i+1)+' '
    name=input(prompt)
    gestNames.append(name)
correctGesture = gestNames[0]
print('name of gesture we need to verify:', correctGesture)


cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    image = cv2.resize(image,(width, height))
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue
    
    # draw bounding box
    image = cv2.rectangle(image, start_point, end_point, (255, 0, 0), 4)

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    Hands=[]
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        Hand=[]
        for landMark in hand_landmarks.landmark:
              Hand.append((int(landMark.x*width),int(landMark.y*height)))
        Hands.append(Hand)

    for h in Hands:
        for i in allPoints:
            cv2.circle(image, h[i], 5, (255,0,255), 3)
    

    # Flip the image horizontally for a selfie-view display.
    image = cv2.flip(image, 1)
    if Hands != []:
        unknownGesture = getDistancesMatrix(Hands[0])
        myGesture = verifyGesture(unknownGesture, gesture_dict, keyPoints, correctGesture, tol)
        #error=findError(knownGesture,unknownGesture,keyPoints)
        cv2.putText(image,myGesture, (25,50), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,0,0), 4)
        
    
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()


# # For static images:
# IMAGE_FILES = []
# with mp_hands.Hands(
#     static_image_mode=True,
#     max_num_hands=2,
#     min_detection_confidence=0.5) as hands:
#   for idx, file in enumerate(IMAGE_FILES):
#     # Read an image, flip it around y-axis for correct handedness output (see
#     # above).
#     image = cv2.flip(cv2.imread(file), 1)
#     # Convert the BGR image to RGB before processing.
#     results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

#     # Print handedness and draw hand landmarks on the image.
#     print('Handedness:', results.multi_handedness)
#     if not results.multi_hand_landmarks:
#       continue
#     image_height, image_width, _ = image.shape
#     annotated_image = image.copy()
#     for hand_landmarks in results.multi_hand_landmarks:
#       print('hand_landmarks:', hand_landmarks)
#       print(
#           f'Index finger tip coordinates: (',
#           f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
#           f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
#       )
#       mp_drawing.draw_landmarks(
#           annotated_image,
#           hand_landmarks,
#           mp_hands.HAND_CONNECTIONS,
#           mp_drawing_styles.get_default_hand_landmarks_style(),
#           mp_drawing_styles.get_default_hand_connections_style())
#     cv2.imwrite(
#         '/tmp/annotated_image' + str(idx) + '.png', cv2.flip(annotated_image, 1))
#     # Draw hand world landmarks.
#     if not results.multi_hand_world_landmarks:
#       continue
#     for hand_world_landmarks in results.multi_hand_world_landmarks:
#       mp_drawing.plot_landmarks(
#         hand_world_landmarks, mp_hands.HAND_CONNECTIONS, azimuth=5)
