import os
import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QDesktopWidget, QTextEdit, QFileDialog 
from PyQt5.QtWebEngineWidgets import QWebEngineView #pip install PyQtWebEngine to be able to import this
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt
from resources import resources #for qrc resources
from screeninfo import get_monitors
from pynput.mouse import Controller
from PIL import ImageGrab
import numpy as np

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Math 2 Latex'
        self.left = 10
        self.top = 10
        self.width = 700
        self.height = 400
        self.img = None
        self.snipWidget = SnipWidget(self) # object of SnipWidget Class
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.centerApp() # user defined

        # Create LaTeX display
        self.webView = QWebEngineView()
        self.webView.setHtml("")
        self.webView.setMinimumHeight(80)
        self.webView.show() # displays latex in a new window

        # Creates Textbox
        self.textbox = QTextEdit(self)
        self.textbox.textChanged.connect(self.displayPrediction)
        self.textbox.setGeometry(50, 180, 600, 80)

        # Creates snip button
        btnSnip = QPushButton('Snip', self)
        btnSnip.setToolTip('This is to snip an image of a math equation')
        btnSnip.setGeometry(100, 300, 200, 50)
        btnSnip.clicked.connect(self.snipImg) 

        # Creates load image button
        btnLoad = QPushButton("Load Image", self)
        btnLoad.setToolTip('This is to load an image of a math equation from a folder locally')
        btnLoad.setGeometry(400, 300, 200, 50)
        btnLoad.clicked.connect(self.loadImg) 

        self.show()
    
    def centerApp(self): # centers application
        qtRectangle = self.frameGeometry() # retrieves geometry of the window
        centerPoint = QDesktopWidget().availableGeometry().center() # gets the center of the screen
        qtRectangle.moveCenter(centerPoint) # moves created window to center
        qPoint = qtRectangle.topLeft()
        self.move(qPoint) # moves current application's window to created window's location


    @pyqtSlot() #decorator function that runs some built-in code (used for buttons) before (and after) snip()'s execution 
    def snipImg(self):
        self.close()
        self.snipWidget.snip()

    def snipImg(self):
        self.close()
        self.snipWidget.snip()

    def returnFromSnip(self, img=None):
         self.show()


    @pyqtSlot()
    def loadImg(self):
        currDirectory = os.path.abspath(os.getcwd()) # gets path of current py file
        imgsDirectory = os.path.join(currDirectory, "tests") # concatenates tests folder to that path
        fname = QFileDialog.getOpenFileName(self, "Open file", imgsDirectory, "Image files (*.jpg *.png)") # "fname" is a tuple consisting of the chosen path e.g. "C:\img.png" and the string "Image files (*.jpg *.png)" 
        self.img = cv2.imread(fname[0])



    @pyqtSlot() 
    def displayPrediction(self, prediction = None):
        if prediction is not None:
            self.textbox.setText("${equation}$".format(equation=prediction))
        else:
            prediction = self.textbox.toPlainText().strip('$')
        print(prediction) #replace 'src=' value below with this: https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML
        pageSource = """
        <html>
            <head>
                <script type="text/javascript" src="qrc:MathJax.js">     
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
    isSnipping = False

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        monitos = get_monitors()
        bboxes = np.array([[m.x, m.y, m.width, m.height] for m in monitos])
        x, y, _, _ = bboxes.min(0)
        w, h = bboxes[:, [0, 2]].sum(1).max(), bboxes[:, [1, 3]].sum(1).max()
        self.setGeometry(x, y, w-x, h-y)

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

        self.mouse = Controller()

    def snip(self):
        self.isSnipping = True
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.show()

    def paintEvent(self, event):
        if self.isSnipping:
            brushColor = (0, 180, 255, 100)
            lw = 3
            opacity = 0.3
        else:
            brushColor = (255, 255, 255, 0)
            lw = 3
            opacity = 0

        self.setWindowOpacity(opacity)
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), lw))
        qp.setBrush(QtGui.QColor(*brushColor))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            QApplication.restoreOverrideCursor()
            self.close()
            self.parent.show()
        event.accept()

    def mousePressEvent(self, event):
        self.startPos = self.mouse.position

        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.isSnipping = False
        QApplication.restoreOverrideCursor()

        startPos = self.startPos
        endPos = self.mouse.position

        x1 = min(startPos[0], endPos[0])
        y1 = min(startPos[1], endPos[1])
        x2 = max(startPos[0], endPos[0])
        y2 = max(startPos[1], endPos[1])

        self.repaint()
        QApplication.processEvents()
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True)
        QApplication.processEvents()

        self.close()
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.parent.returnFromSnip(img)





if __name__ == '__main__':
    appPtr = QtCore.QCoreApplication.instance() # this pointer and the if statement are done to allow this to be run in an .ipynb file
    if appPtr is None:
        app = QApplication(sys.argv) # super class
    ex = App() # subclass
    sys.exit(app.exec_()) # executing super class which executes subclass 
    # app.exec_() runs a GUI event loop that waits for user actions (events) 
    # and dispatches them to the right widget for handling.
