import pytesseract
import cv2, os, sys
from PIL import Image
import PyQt5
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
import glob

# In python we can either use / or \\ for paths

language_path = "C:\\Users\\asif\\AppData\\Local\\Programs\\Tesseract-OCR\\tessdata\\"
language_path_list = glob.glob(language_path+"*.traineddata")

language_names_list = []

for path in language_path_list:
    base_name = os.path.basename(path)
    base_name = os.path.splitext(base_name)[0]
    language_names_list.append(base_name)

print ('Named List: ',language_names_list)

font_list = []
font=2

for font in range(50):
    font+=2
    font_list.append(str(font))

print ('Font List: ',font_list)

class OCR_App(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('main.ui', self)
        self.image = None
        
        self.ui.pushButton.clicked.connect(self.open)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle,self)
        self.ui.label_2.setMouseTracking(True)
        self.ui.label_2.installEventFilter(self)
        self.ui.label_2.setAlignment(PyQt5.QtCore.Qt.AlignTop)

        self.language = 'eng'
        self.comboBox.addItems(language_names_list)
        self.comboBox.currentIndexChanged['QString'].connect(self.update_now)
        self.comboBox.setCurrentIndex(language_names_list.index(self.language))

        self.font_size = '20'
        self.text = ''
        self.comboBox_2.addItems(font_list)
        self.comboBox_2.currentIndexChanged['QString'].connect(self.update_font_size)
        self.comboBox_2.setCurrentIndex(font_list.index(self.font_size))

        self.ui.textEdit.setFontPointSize(int(self.font_size))
        self.setAcceptDrops(True)
    
    def update_now(self,value):
        self.language = value
        print('Language Selected as:',self.language)

    def update_font_size(self,value):
        self.font_size = value
        self.ui.textEdit.setFontPointSize(int(self.font_size))
        self.ui.textEdit.setText(str(self.text))
    
    def open(self):
        filename = QFileDialog.getOpenFileName(self,'Select File')
        self.image = cv2.imread(str(filename[0]))
        frame = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        image = QImage(frame,frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
        self.ui.label_2.setPixmap(QPixmap.fromImage(image))
  
    # Takes the cropped image as input
    def image_to_text(self,crop_cvimage):
        gray = cv2.cvtColor(crop_cvimage,cv2.COLOR_BGR2GRAY) # convert the image to grayscale
        gray = cv2.medianBlur(gray,1) # Apply the median filter to remove noise
        crop = Image.fromarray(gray)
        text = pytesseract.image_to_string(crop,lang = self.language) # apply pytesseract to convert image into text
        print('Text:',text)
        return text

# The event filter to get the cropped image from user selection
    def eventFilter(self,source,event):
        width = 0
        height = 0
        if (event.type() == QEvent.MouseButtonPress and source is self.ui.label_2):
            self.org = self.mapFromGlobal(event.globalPos())
            self.left_top = event.pos() # when mouse button is pressed, we get top left position of rectangular region
            self.rubberBand.setGeometry(QRect(self.org,QSize()))
            self.rubberBand.show() # here we will start showing the rectangle

# if now the mouse is moved and the button is kept pressed we will keep updating the geometry of the rectangle
        elif (event.type() == QEvent.MouseMove and source is self.ui.label_2):
            if self.rubberBand.isVisible():
                self.rubberBand.setGeometry(QRect(self.org,self.mapFromGlobal(event.globalPos())).normalized())

# now if the mouse button is released we will hide the rectangle and get the right geometry the x1
# and y1 are coordinates of the top left corner point.
# By knowing the width and height we can get the coordinates of the bottom right point as x2 and y2
        elif(event.type() == QEvent.MouseButtonRelease and source is self.ui.label_2):
            if self.rubberBand.isVisible():
                self.rubberBand.hide()
                rect = self.rubberBand.geometry()
                self.x1 = self.left_top.x()
                self.y1 = self. left_top.y()
                width = rect.width()
                height = rect.height()
                self.x2 = self.x1+ width
                self.y2 = self.y1+ height
# after getting a valid image region we will send it to the image to text function, 
# it will give us the text which we can place on the text edit widget and finally we will return the event filter
# the width and height are initialized as well
            if width >=10 and height >= 10  and self.image is not None:
                self.crop = self.image[self.y1:self.y2, self.x1:self.x2]
                cv2.imwrite('cropped.png',self.crop)
                self.text = self.image_to_text(self.crop) # cropped image is passed to image to text function, that returns the text
                self.ui.textEdit.setText(str(self.text))
            else:
                self.rubberBand.hide()
        else:
            return 0
        return QWidget.eventFilter(self,source,event)

app = QtWidgets.QApplication(sys.argv)
mainWindow = OCR_App()
mainWindow.show()
sys.exit(app.exec_())

