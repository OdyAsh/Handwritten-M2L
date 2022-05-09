import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView #pip install PyQtWebEngine to be able to import this
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from resources import resources

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Math 2 Latex'
        self.left = 10
        self.top = 10
        self.width = 700
        self.height = 400
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


    @pyqtSlot() #decorator function that runs some built-in code before (and after) snip()'s execution 
    def snipImg(self):
        print('CODE TO SNIP IMAGE')

    @pyqtSlot()
    def loadImg(self):
        print('CODE TO load IMAGE FROM LOCAL FILE')

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

if __name__ == '__main__':
    appPtr = QtCore.QCoreApplication.instance() # this pointer and the if statement are done to allow this to be run in an .ipynb file
    if appPtr is None:
        app = QApplication(sys.argv) # super class
    ex = App() # subclass
    sys.exit(app.exec_()) # executing super class which executes subclass 
    # app.exec_() runs a GUI event loop that waits for user actions (events) 
    # and dispatches them to the right widget for handling.
