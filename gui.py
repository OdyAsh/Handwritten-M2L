import os
import sys
import cv2
import pickle
from imgPreProcess import extractSymbols # Imports extractSymbols() from imgPreProcess.py to process the input image to be compatible with the NN model
from resources import resources # Imports resources.py for qrc resources to work
from tensorflow import keras
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QDesktopWidget, QTextEdit, QFileDialog 
from PyQt5.QtWebEngineWidgets import QWebEngineView # pip install PyQtWebEngine to be able to import this
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from screeninfo import get_monitors
from pynput.mouse import Controller
from PIL import ImageGrab
import numpy as np
# App object here is the environment. The info on the monitor is also considered from the enviornment since the input images are taken from it
class App(QMainWindow): # Using QMainWindow as super class because it contains methods not present in the base class "QWidgets" like "self.setCentralWidget()"

    def __init__(self):
        super().__init__()
        self.title = 'Math 2 Latex'
        self.left = 10
        self.top = 10
        self.width = 700
        self.height = 400
        self.img = None
        self.webView = None
        self.textbox = None
        self.snipWidget = SnipWidget(self) # object of SnipWidget Class, "self" here is this current "App" object that will be sent to the created SnipWidget object
        self.model = keras.models.load_model("ThennModel") 
        with open("numsToLatex.pickle", 'rb') as f:
            self.numsToLatex = pickle.load(f)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        QApplication.setWindowIcon(QtGui.QIcon('resources/Pi-Black.svg')) # ":/icons/Pi-Black.svg" (from qrc resources) didn't work
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.centerApp() # user defined

        # Create LaTeX display
        self.webView = QWebEngineView()
        self.webView.setHtml("")
        self.webView.setMinimumHeight(40)

        # Creates Textbox
        self.textbox = QTextEdit(self)
        self.textbox.textChanged.connect(self.displayPrediction)
        self.textbox.setMinimumHeight(40)

        # Creates snip button
        btnSnip = QPushButton('Snip', self)
        btnSnip.setToolTip('This is to snip an image of a math equation')
        btnSnip.setMinimumHeight(40)
        btnSnip.clicked.connect(self.snipImg) 

        # Creates load image button
        btnLoad = QPushButton("Load Image", self)
        btnLoad.setToolTip('This is to load an image from a folder locally')
        btnLoad.setMinimumHeight(40)
        btnLoad.clicked.connect(self.loadImg) 

        # Create Vertical & Horizontal layouts to main window (centralWidget)
        centralWidget = QWidget()
        centralWidget.setMinimumWidth(200)
        self.setCentralWidget(centralWidget)

        vBox = QVBoxLayout(centralWidget)
        vBox.addWidget(self.webView, stretch=4)
        vBox.addWidget(self.textbox, stretch=2)

        hBox = QHBoxLayout()
        hBox.addWidget(btnSnip)
        hBox.addWidget(btnLoad)
        vBox.addLayout(hBox)

        self.show()
    
    def centerApp(self): # centers application
        qtRectangle = self.frameGeometry() # retrieves geometry of the window
        centerPoint = QDesktopWidget().availableGeometry().center() # gets the center of the screen
        qtRectangle.moveCenter(centerPoint) # moves created window to center
        qPoint = qtRectangle.topLeft()
        self.move(qPoint) # moves current application's window to created window's location


    @pyqtSlot() #decorator function that runs some built-in code (used for buttons) before (and after) snip()'s execution 
    def snipImg(self): # Sensor (Perceptor) Function
        self.close()
        self.snipWidget.snip()


    @pyqtSlot()
    def loadImg(self): # Sensor (Perceptor) Function
        currDirectory = os.path.abspath(os.getcwd()) # gets path of current py file
        imgsDirectory = os.path.join(currDirectory, "tests") # concatenates tests folder to that path
        fname = QFileDialog.getOpenFileName(self, "Open file", 
                                            imgsDirectory, 
                                            "Image files (*.jpg *.png)") # "fname" is a tuple consisting of the chosen path e.g. "C:\img.png" and the string "Image files (*.jpg *.png)" 
        self.img =  cv2.imread(fname[0]) # setting the img attribute in case it will be used later
        self.predictLatex(self.img)

    def predictLatex(self, img=None): # Agent Function
        self.show() # Displays the main GUI window after it has been closed by snipImg()
        symbols = extractSymbols(imgOrig=img, showSteps=True, medFilter=True, verticalSymbols=False) # Processes image (by returning list of cropped math symbols) to be a compatible input for the NN model
        prediction = ""
        for symbol in symbols:
            label = np.argmax(self.model.predict(symbol))
            latex = self.numsToLatex[label]
            print(latex) # Debugging
            prediction += latex + ' '
        prediction = prediction.replace('\X', 'X')
        print(prediction)
        self.displayPrediction(prediction)


    @pyqtSlot() 
    def displayPrediction(self, prediction = None): # Actuator Function
        if prediction is not None:
            self.textbox.setText("${equation}$".format(equation=prediction))
        else:
            prediction = self.textbox.toPlainText().strip('$')
        pageSource = """
        <html>
            <head>
                <script type="text/javascript" src="qrc:MathJax.js"> <!-- if qrc is not working, replace 'src=' value with this: https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML -->
                </script>
            </head>
            <body>
                <p>
                    <mathjax style="font-size:2.3em"> 
                        $${equation}$$
                    </mathjax>
                </p>
            </body>
        </html>
        """.format(equation=prediction)
        
        self.webView.setHtml(pageSource)



class SnipWidget(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.isSnipping = False
        self.parent = parent # "parent" here is the "App" object that called this class

        monitors = get_monitors() # gets monitor's x and y position of top left rectangle corner, and the rectangle's (montior's) width and height
        bboxes = np.array([[m.x, m.y, m.width, m.height] for m in monitors]) # the for loop is in case there are multiple monitors
        x, y, _, _ = bboxes.min(0) # retrieves the positions of the smallest x,y pair ("0" means sort on 0-axis: [1,2,3,4] and [1,2,0,8] will return [1,2,3,4] array as 0 < 3 but 4 < 8, while min(1) will return [1,0])
        w, h = bboxes[:, [0, 2]].sum(1).max(), bboxes[:, [1, 3]].sum(1).max() # obtains max xPoint+width and max yPoint+height which corresponds to a width and height covering all the monitors
        self.setGeometry(x, y, w-x, h-y) # sets the new snipping window with obtained x,y,w,h

        self.startPos = None
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

        self.mouse = Controller() # a controller for sending virtual mouse events to the system. Useful attribute: "position"

    def snip(self): # Sensor (Perceptor) Function
        self.isSnipping = True
        self.setWindowFlags(Qt.WindowStaysOnTopHint) # hints are used to customize the appearance of top-level windows, while "WindowStaysOnTopHint" is a flag that Informs the window system that the snipping window should stay on top of all other windows
        QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor)) # changes cursor to look like a "+" (Cross Cursor)

        self.show() # displays the snipping window

    def paintEvent(self, event):
        if self.isSnipping:
            brushColor = (51, 153, 255, 100) # red, green, blue, alpha
            opacity = 0.3
        else:
            brushColor = (255, 255, 255, 0)
            opacity = 0
        lineWidth = 3

        self.setWindowOpacity(opacity)
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('blue'), lineWidth)) # "lineWidth" means the line width of the rectangle's border
        qp.setBrush(QtGui.QColor(*brushColor)) # "*" unpacks the tuple to be 4 arguments
        qp.drawRect(QtCore.QRect(self.begin, self.end)) # draws a rectangle based on top left and bottom right corners of the rectangle

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape: # if escape key is pressed, close snipping window and return to main GUI
            QApplication.restoreOverrideCursor() # restores the original cursor instead of "+"
            self.close()
            self.parent.show()
        event.accept() # this means to pass the event of the current keyboard click which is equivalent to releasing mouse click so it calls mouseReleaseEvent()

    def mousePressEvent(self, event):
        self.startPos = self.mouse.position # (x,y) with respect to the monitor
        self.begin = event.pos() # (x,y) with respect to the snipping window opened Which is approximately the same size as the monitor
        self.end = self.begin # sets begin and end points to same point since we just pressed left click and didn't move the mouse
        self.update() # updates the window and the rectangle (for example, calls functions like paintEvent())

    def mouseMoveEvent(self, event):
        self.end = event.pos() # changes end point (top left or bottom right corner) to current mouse position in the snipping window
        self.update()

    def mouseReleaseEvent(self, event):
        self.isSnipping = False
        QApplication.restoreOverrideCursor() # restores the original cursor instead of "+"

        startPos = self.startPos
        endPos = self.mouse.position

        # this is to make sure (x1,y1) is the top left corner and (x2,y2) is the bottom right corner of the rectangle
        x1 = min(startPos[0], endPos[0])
        y1 = min(startPos[1], endPos[1])
        x2 = max(startPos[0], endPos[0])
        y2 = max(startPos[1], endPos[1])


        self.repaint() # same as self.update() but repaint() forces an immediate repaint, whereas update() schedules a paint event for when Qt next processes events.
        QApplication.processEvents() # function that returns after all available events have been processed. Done to make sure the image is obtained based on the very last rectangle drawn on the screen
        self.parent.img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True) # extracts a PIL image from the created rectangle's area
        QApplication.processEvents()

        self.close() # closes the snipping window that approximately covers the monitor
        self.begin = QtCore.QPoint() # returns rectangle to just a point, in order for the previous rectangle not to appear when clicking on the snip button again
        self.end = QtCore.QPoint()

        self.parent.predictLatex(self.parent.img) # calls the predictLatex() function in "App" parent object and passes the snipped image for the called function to predict the latex equivalent of that image






if __name__ == '__main__':
    appPtr = QtCore.QCoreApplication.instance() # this pointer and the if statement are done to allow this to be run in an .ipynb file
    if appPtr is None:
        app = QApplication(sys.argv) # super class
    ex = App() # subclass
    sys.exit(app.exec_()) # executing super class which executes subclass 
    # app.exec_() runs a GUI event loop that waits for user actions (events) 
    # and dispatches them to the right widget for handling.
