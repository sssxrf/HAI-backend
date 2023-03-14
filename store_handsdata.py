import cv2
import mediapipe as mp
import numpy as np

# parameters:
width = 540
height = 360
keyPoints = [0,1,4,5,9,13,17,8,12,16,20]
allPoints = list(range(0, 21))

#mp initial
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

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

def findGesture(unknownGesture, knownGestures, keyPoints, gestNames, tol):
    errorArray=[]
    for i in range(0,len(gestNames)):
        error=findError(knownGestures[i], unknownGesture, keyPoints)
        errorArray.append(error)
    errorArray = np.array(errorArray)
    errorMin=np.min(errorArray)
    minIndex = np.argmin(errorArray)
    if errorMin<tol:
        gesture=gestNames[minIndex]
    if errorMin>=tol:
        gesture='Unknown'
    return gesture


numGest=int(input('How Many Gestures Do You Want? '))
 
gestNames=[]
knownGestures = []
trainCnt = 0
train = True
tol = 1500
stored_handsdata = []

for i in range(0, numGest, 1):
    prompt='Name of Gesture #'+str(i+1)+' '
    name=input(prompt)
    gestNames.append(name)
print(gestNames)


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    # height, width, _ = image.shape
    # image = cv2.resize(image,(width, height))
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

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
    if train==True:
        # Flip the image horizontally for a selfie-view display.
        image = cv2.flip(image, 1)
        if Hands != []:
            print('Please Show Gesture ',gestNames[trainCnt],': Press t when Ready')
            if cv2.waitKey(1) & 0xff==ord('t'):
                stored_handsdata.append(Hands[0])
                knownGesture=getDistancesMatrix(Hands[0])
                knownGestures.append(knownGesture)
                trainCnt=trainCnt+1
                if trainCnt==numGest:
                    with open(r'D:/umich_course/2023winter/HCI-AI/Final Project\backend/HAI-backend/gesturedatas/gesture_info.txt', 'w') as fp:
                        for index in range(numGest):
                            fp.write("%s\n" % gestNames[index])
                            fp.write('\n'.join('%s %s' % x for x in stored_handsdata[index]))
                            fp.write("\n")
                        
                        print('Gesture storage Done')
                    train=False
    if train == False:
        # Flip the image horizontally for a selfie-view display.
        image = cv2.flip(image, 1)
        if Hands != []:
            unknownGesture=getDistancesMatrix(Hands[0])
            myGesture=findGesture(unknownGesture,knownGestures,keyPoints,gestNames,tol)
            #error=findError(knownGesture,unknownGesture,keyPoints)
            cv2.putText(image,myGesture,(50,100),cv2.FONT_HERSHEY_SIMPLEX,3,(255,0,0),4)
        
    
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
