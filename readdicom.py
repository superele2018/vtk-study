import vtk,scipy,os,sys
import dicom
import time
import six
import numpy as np
from vtk import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget,QLabel,QMainWindow
from PyQt5.QtGui import QPixmap,QImage,QMatrix2x2
from PyQt5.uic import loadUi
import skimage
from skimage import data
from qimage2ndarray import array2qimage,gray2qimage
from vtk.util import numpy_support

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        loadUi('vtk.ui', self)
        self.slices = load_scan('D:\Anaconda\workspace\pytest\patient')
        self.image_shape=self.slices[0].pixel_array.shape
        print(self.image_shape)
        self.label.resize(400,400)
        print(len(self.slices))
        self.index = 0
        self.display()
        # self.button.clicked.connect(self.slot1)
        self.show()
    def display(self):
        self.index+=1
        print(self.index)
        # self.imagedata = gray2qimage(self.slices[self.index].pixel_array, normalize=(0, 255))
        self.imagedata=QImage()
        self.imagedata.load('D:\Anaconda\workspace\pytest\\1.jpg')
        self.pixmap=QPixmap('D:\Anaconda\workspace\pytest\\1.jpg')
            # .fromImage(self.imagedata)
        self.pixmap.scaled(300,300,QtCore.Qt.IgnoreAspectRatio,QtCore.Qt.FastTransformation)
        time.sleep(3)
        self.label.setPixmap(self.pixmap)
        # self.label.setAlignment(QtCore.Qt.AlignCenter)
        # print(self.label.sizeHint())

    def wheelEvent(self, event):
        max = 512
        min = 200
        if event.angleDelta().y() == 120:
            # 滚动3%
            # new = self.label.width()+ max * 0.03
            new = self.imagedata.width() + max * 0.03
            if new > max:
                new = max
            # self.emit(self.slideMoved, new)
        elif event.angleDelta().y()  == -120:
            # new = self.label.width() - max * 0.03
            new = self.imagedata.width() + max * 0.03
            if new < min:
                new = min
        self.imagedata.scaled(new, new)


    def slot1(self):
        self.display()



def load_scan(path):
    slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
    slices.sort(key = lambda x: int(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices

def loadFileInformation(filename):
    information = {}
    ds = dicom.read_file(filename)
    information['PatientID'] = ds.PatientID
    information['PatientName'] = ds.PatientName
    information['PatientBirthDate'] = ds.PatientBirthDate
    information['PatientSex'] = ds.PatientSex
    information['StudyID'] = ds.StudyID
    information['StudyDate'] = ds.StudyDate
    information['StudyTime'] = ds.StudyTime
    information['InstitutionName'] = ds.InstitutionName
    information['Manufacturer'] = ds.Manufacturer
    information['NumberOfFrames'] = ds.NumberOfFrames
    return information




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()


    # loadFromData (bdata)
    sys.exit(app.exec_())
