# ---------------------------- THIS IS THE BEGINNING OF APP2 -------------------------------------------

from flask import Flask, render_template, Response, request
import cv2
import mediapipe as mp
import pickle
import numpy as np
import random
from werkzeug.utils import secure_filename
import os
from pathlib import Path

#Instantiating the flask class as a variable and assigning that variable to a new variable called app [1]
application = Flask(__name__)
#Creating a list of file extensions that will be accepted by our flask app per the recommendation of Miguel Grinberg's article and flask documentation [22] [26]
application.config["ALLOWED_EXTENSIONS"] = [".jpeg", ".jpg", ".png", ".gif"]
#Designating a folder where we want our approved files to be uploaded [22] [26]
application.config['UPLOAD_FOLDER'] = 'static/'
#app = application

#loading our best model using pickle and assigning it to the variable model to use in our gen frames function
model_dict = pickle.load(open('svc_model.pkl', 'rb'))
model = model_dict['model']

#creating our label dictionary, this was created using inverse transform function of the label encoder class
label_dict = { 0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'K', 10:'L', 
11:'M', 12:'N', 13:'O', 14:'P', 15:'Q', 16:'R', 17:'S', 18:'T', 19:'U', 20:'V', 21:'W', 22:'X', 23:'Y', 
24:'8', 25:'5', 26:'4', 27:'9', 28:'1', 29:'7', 30:'6', 31:'10', 32:'3', 33:'2'}

#creating an empty list variable that is going to serve as our global variable [16]
sign = []
image_width = []
image_height = []
#creating a function called sign that takes a random value from list [4]
def rand_sign():
    global sign
    sign = random.choice(label_dict)
    return sign

#creating a function that takes the landmark data and puts them appends them together and returns that list [4][5]
def ret_landmark_list(hand_landmarks):
    #Creating an empty list for our landmarks [5]
    landmark_point = []
    # Creating a for loop that iterates through our landmarks returns the value and appends to our list [10][11][12]
    for _, landmark in enumerate(hand_landmarks.landmark):
        #After reading the mediapipe issues responses for handtracking specifically mcclanahoochie (Member of Google) and Tectu's (Joel Bodenmann) responses
        # i decided to normalize the x and y coords by image height and width per their recommendation [13]
        landmark_x = (landmark.x * image_width)
        landmark_y = (landmark.y * image_height)
        landmark_z = landmark.z
        # appending the points to the list as floats [11][14]
        landmark_point.append(float(landmark_x))
        landmark_point.append(float(landmark_y))
        landmark_point.append(float(landmark_z))
    #returning the complete list of landmarks [10]
    return landmark_point

#using the variable for our mediapipe utilities via the sample code from their docs [2] 
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

#The gen_frames function is derived from the example code from Grinberg, Lokhotia's article, and Mediapipe docs altered for our specific use case [2] [3] [4] 
def gen_frames():
    #calling our predefined global variables [16]
    global image_height, image_width
    #using the mp_hands variable to set our parameters for mediapipe [2]
    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5) as hands:
        # Reading in the image using its path and cv2 image read flipping it and getting our results and the dimensions [2] [23] [24]      
        frame = cv2.imread(str(Path('static/image.jpg')), 1)
        frame = cv2.flip(frame, 1)
        results = hands.process(frame)
        image_height, image_width, c = frame.shape
        #If statement to get the hand landmarks from the frame [2]
        if results.multi_hand_landmarks:
            #For loop to iterate through the landmarks and using the drawing utility to draw them on the frame [2]
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                #using our function to extract landmarks
                lm = ret_landmark_list(hand_landmarks)
                #using our best model to make a prediction on the extracted landmarks [25]
                prediction = model.predict([np.array(lm)])
                #Using the label dictionary above and slicing for our prediction value [10] 
                pred_char = label_dict[int(prediction[0])]
                #Using the OpenCV put text class to put our predicted character on the frame of our output [15]
                cv2.putText(frame, pred_char, (20,50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 200), 3, cv2.LINE_AA)  
    #retrieving the frame and using cv2.imencode to encode the image into a memory buffer [17]
    ret, buffer = cv2.imencode('.jpg', frame)
    #taking the new encoded image converting it to bytes and assigning it to the frame variable [18]
    frame = buffer.tobytes()
    # calling yeild frame to show result [3]
    yield (frame)

#Creating another gen frames function to use for the practice page [2] [3] [4]
def gen_frames2():
    #calling our predefined global variables [16]
    global image_height, image_width
    #using the mp_hands variable to set our parameters for mediapipe [2]
    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5) as hands:
        # Reading in the image using its path and cv2 image read flipping it and getting our results and the dimensions [2] [23] [24]
        frame = cv2.imread(str(Path('static/image.jpg')), 1)
        frame = cv2.flip(frame, 1)
        results = hands.process(frame)
        image_height, image_width, c = frame.shape
        #If statement to get the hand landmarks from the frame [2]
        if results.multi_hand_landmarks:
            #For loop to iterate through the landmarks and using the drawing utility to draw them on the frame [2]
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                #Using the retrieve landmarks function to extract the landmarks from the frame 
                lm = ret_landmark_list(hand_landmarks)
                #using our best model to make a prediction on the extracted landmarks [25]
                prediction = model.predict([np.array(lm)])
                #Using the label dictionary above and slicing for our prediction value [10]
                pred_char = label_dict[int(prediction[0])]
                #Creating an if statement to take our global sign variable and compare it to our prediction to return a right or wrong output [11]
                if str(sign) == str(pred_char):
                    c = 'Correct'
                    #Using the OpenCV put text class to put our correct value on the frame of our output [15]
                    cv2.putText(frame, c, (20,50),cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 200, 0), 3, cv2.LINE_AA)
                else:
                    w = 'Try Again'
                    #Using the OpenCV put text class to put our incorrect value on the frame of our output [15]
                    cv2.putText(frame, w, (20,50),cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 200), 3, cv2.LINE_AA)
    #retrieving the frame and using cv2.imencode to encode the image into a memory buffer [17]
    ret, buffer = cv2.imencode('.jpg', frame)
    #taking the new encoded image converting it to bytes and assigning it to the frame variable [18]
    frame = buffer.tobytes()
    # calling yeild frame to show result [3]
    yield (frame)  


#creating our home page [5]
@application.route('/')
def index():
    return render_template('index.html')
#creating the about page [5]
@application.route('/About')
def about():
    return render_template('about.html')
#creating the display page for the playground [5]
@application.route('/Playground', methods = ['GET', 'POST'])
#Creating a function called play that takes requests from the user to start and stop the camera
def play():
    global frame
    #If statement that that takes the POST request method [19] [20] [21] [8]
    if request.method == 'POST':
        # takes a file from our request form that the user uploaded [26]
        file = request.files['img']
        #takes that file and saves it in our desired predefined path and uses a secure filename [22] [26] [27] [29]
        file.save(os.path.join(application.config["UPLOAD_FOLDER"], secure_filename("image.jpg")))
    #returning the playground template [11]
    return render_template("playground.html")

#Creating the routing that will be called in the playground page to display the image input [5]
@application.route('/freeplay')
#function that returns the the generate frames  [3]
def display():
    #returns a response that calls gen frames [3]
    return Response(gen_frames())
    
#Creating the routing that will be called in the practice page to display out image input [5]
@application.route('/forprac')
#function that will be used for our practice page [11]
def framebyframe():
    #If statement that that takes the POST request "random" and returns the global variable of sign to generate output for the user [19] [20] [8]
    if request.form.get('random') == 'Random Sign':
        #setting sign equal to our predefined function
        sign = rand_sign()
        #returning the gen frames2 function that will take the sign variable check if it is equal to our user input gesture and return right or wrong [11] [19] [20] [28]
        return Response(gen_frames2(),sign=sign)
    #returning the base gen frame2 function [28]
    return Response(gen_frames2())

@application.route('/Practice', methods = ['GET', 'POST'])
#Creating a function called play that takes requests from the user to start and stop the camera
def prac():
    #calling our global sign function [16]
    global sign
    #If statement that that takes the POST request method [19] [20] [21] [8]
    if request.method == 'POST':
        #If statement that that takes the POST request "random" and returns the global variable of sign to generate output for the user [19] [20] [8]
        if request.form.get('random') == 'Random Sign':
            #setting sign equal to our function above
            sign = rand_sign()
            ## takes a file from our request form that the user uploaded [26]
            # file = request.files['img']
            # #takes that file and saves it in our desired predefined path and uses a secure filename [22] [26] [27] [29]
            # file.save(os.path.join(application.config["UPLOAD_FOLDER"], secure_filename("image.jpg") ))
            return render_template('practice.html',sign=sign)
        ## takes a file from our request form that the user uploaded [26]
        file = request.files['img']
        #takes that file and saves it in our desired predefined path and uses a secure filename [22] [26] [27] [29]
        file.save(os.path.join(application.config["UPLOAD_FOLDER"], secure_filename("image.jpg") ))
    #returning the practice template [11]
    return render_template("practice.html", sign=sign)


if __name__ == '__main__':
    application.run(debug=True)







''' References:
    [1] “Project Layout — Flask Documentation (3.0.x),” flask.palletsprojects.com. https://flask.palletsprojects.com/en/latest/tutorial/layout/ (accessed Sep. 22, 2023).
    [2] “layout: forward target: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker title: Hands parent: MediaPipe Legacy Solutions nav_order: 4 — MediaPipe v0.7.5 documentation,” mediapipe.readthedocs.io. https://mediapipe.readthedocs.io/en/latest/solutions/hands.html
    [3] M. Grinberg, “Video Streaming with Flask,” blog.miguelgrinberg.com. https://blog.miguelgrinberg.com/post/video-streaming-with-flask
    [4] N. Lakhotia, “Video Streaming in Web Browsers with OpenCV & Flask,” Medium, Jan. 11, 2021. https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00
    [5] “Blueprints and Views — Flask Documentation (3.0.x),” flask.palletsprojects.com. https://flask.palletsprojects.com/en/latest/tutorial/views/ (accessed Sep. 22, 2023).
    [6] “Business Frontpage - Bootstrap 5 Business Home Page Template,” Start Bootstrap. https://startbootstrap.com/template/business-frontpage (accessed Sep. 23, 2023).
    [7] “Get video dimension in python-opencv,” Stack Overflow. https://stackoverflow.com/questions/39953263/get-video-dimension-in-python-opencv (accessed Sep. 26, 2023).
    [8] “OpenCV: cv::VideoCapture Class Reference,” docs.opencv.org. https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html#aa6480e6972ef4c00d74814ec841a2939 (accessed Sep. 26, 2023).
    [9] “OpenCV: Flags for video I/O,” docs.opencv.org. https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#gaeb8dd9c89c10a5c63c139bf7c4f5704d
    [10] “Built-in Functions — Python 3.8.3 documentation,” docs.python.org. https://docs.python.org/3/library/functions.html
    [11] “4. More Control Flow Tools,” Python documentation. https://docs.python.org/3/tutorial/controlflow.html#defining-functions
    [12] D. Chosnek, “How To Use Underscore (_) Properly in Python,” Medium, Jan. 05, 2023. https://betterprogramming.pub/how-to-use-underscore-properly-in-python-37df5e05ba4c (accessed Sep. 19, 2023).
    [13] “Hand tracking landmarks - Z value range · Issue #742 · google/mediapipe,” GitHub. https://github.com/google/mediapipe/issues/742#issuecomment-639104199 (accessed Sep. 19, 2023).
    [14] “5. Data Structures — Python 3.8.3 documentation,” docs.python.org. https://docs.python.org/3/tutorial/datastructures.html
    [15] “OpenCV: Drawing Functions,” docs.opencv.org. https://docs.opencv.org/4.x/d6/d6e/group__imgproc__draw.html
    [16] “Programming FAQ — Python 3.10.0 documentation,” docs.python.org. https://docs.python.org/3/faq/programming.html#what-are-the-rules-for-local-and-global-variables-in-python
    [17] “OpenCV: Image file reading and writing,” docs.opencv.org. https://docs.opencv.org/4.x/d4/da8/group__imgcodecs.html#ga461f9ac09887e47797a54567df3b8b63 (accessed Oct. 02, 2023).
    [18] “array — Efficient arrays of numeric values,” Python documentation. https://docs.python.org/3/library/array.html?highlight=tobytes#array.array.tobytes (accessed Oct. 02, 2023).
    [19] “Quickstart — Flask Documentation (1.1.x),” flask.palletsprojects.com. https://flask.palletsprojects.com/en/1.1.x/quickstart/
    [20] W3Schools, “HTTP Methods GET vs POST,” W3schools.com, 2019. https://www.w3schools.com/tags/ref_httpmethods.asp
    [21] “How to add action buttons in Flask – Predictive Hacks.” https://predictivehacks.com/?all-tips=how-to-add-action-buttons-in-flask
    [22] M. Grinberg, “Handling File Uploads With Flask,” blog.miguelgrinberg.com. https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
    [23] “pathlib — Object-oriented filesystem paths — Python 3.9.4 documentation,” docs.python.org. https://docs.python.org/3/library/pathlib.html
    [24] “OpenCV: Image file reading and writing,” docs.opencv.org. https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html#gabbc7ef1aa2edfaa87772f1202d67e0ce (accessed Oct. 13, 2023).
    [25] scikit-learn developers, “sklearn.svm.SVC — scikit-learn 0.22 documentation,” Scikit-learn.org, 2019. https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html
    [26] “Uploading Files — Flask Documentation (1.1.x),” flask.palletsprojects.com. https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
    [27] “os.path — Common pathname manipulations — Python 3.9.1 documentation,” docs.python.org. https://docs.python.org/3/library/os.path.html
    [28] “API — Flask Documentation (3.0.x),” flask.palletsprojects.com. https://flask.palletsprojects.com/en/3.0.x/api/
    [29] “werkzeug.secure_filename — Flask API,” tedboy.github.io. https://tedboy.github.io/flask/generated/werkzeug.secure_filename.html (accessed Oct. 13, 2023).

'''    