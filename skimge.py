import vtk,scipy,os,sys
import dicom
import time
import six
import numpy as np
import matplotlib.pyplot as plt
from vtk import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget,QLabel,QMainWindow
from PyQt5.QtGui import QPixmap,QImage,QMatrix2x2,QIcon,QBrush,QPalette
from PyQt5.uic import loadUi
from scipy import ndimage as ndi
from skimage import data,io,filters,util,transform,feature,morphology,color
from PIL import Image,ImageQt,ImageEnhance
from qimage2ndarray import array2qimage,gray2qimage
from vtk.util import numpy_support

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        loadUi('vtk.ui', self)
        self.ctrlPressed=False
        self.slices = load_scan('/home/sourayi/桌面/data')
        self.image_shape=self.slices[0].pixel_array.shape
        self.maxslice=len(self.slices)
        print(self.image_shape)
        self.scale=1.0
        self.label.resize(512,512)
        self.label_2.resize(512,512)
        self.setFixedSize(1300,580)
        self.index =49
        self.filter='sobel'
        self.refrehdata()
        self.thresholdvalue=1
        self.display()
        self.button.clicked.connect(self.slot1)
        self.threshold_slider.valueChanged.connect(self.slot_threshold)
        # self.setStyleSheet('background-image:url(D:\Anaconda\workspace\pytest\\background.PNG)')
        self.setWindowTitle('DICOM')
        self.setAutoFillBackground(True)
        pixmap = QPixmap('D:\Anaconda\workspace\pytest\\background.PNG').scaled(1300,600)
        palette=self.palette()
        palette.setBrush(QPalette.Background, QBrush(pixmap))
        self.setPalette(palette)

        self.setWindowIcon(QIcon('D:\Anaconda\workspace\pytest\\background.PNG'))
        self.show()

    def slot_threshold(self,value):
        new_threshold=self.threshold_slider.value()+1
        self.label_thresholdvalue.setText(str(new_threshold)+'%')
        self.thresholdvalue=new_threshold
        self.refrehdata()
        self.display()



    def refrehdata(self):
        self.origin_array = np.uint8(self.slices[self.index].pixel_array)
        self.filter_array = self.slices[self.index].pixel_array
        self.filter_array = self.myfilter(self.filter_array)
        # self.filter_array = transform.rescale(self.filter_array, self.scale)

    def myfilter(self,data):
        if self.filter=='sobel':
            return util.img_as_int(filters.sobel(data))
        elif self.filter=='otsu':
            thresh=filters.threshold_otsu(data)
            return util.img_as_ubyte(data>thresh)
        elif self.filter=='阈值分割':
            thresh=self.thresholdvalue*data.max()/100.0
            return util.img_as_ubyte(data>thresh)
        elif self.filter=='canny edge':
            temp=util.img_as_ubyte(feature.canny(data,low_threshold=30,high_threshold=40))
            return temp
        elif self.filter=='watershed':
            mask=util.img_as_ubyte(filters.gaussian_filter(data, 0.4))
            markers=feature.canny(data,low_threshold=30,high_threshold=40)
            markers=ndi.label(markers)[0]
            idata=filters.rank.gradient(data, morphology.disk(1))
            temp=morphology.watershed(data,markers,mask=mask)
            # hsv=color.convert_colorspace(temp,'L','RGB')
            # io.imshow(hsv)
            return temp
        elif self.filter=='test':
            data=util.img_as_ubyte(filters.median(data,morphology.disk(2)))
            return data




    def display(self):
        self.fitler_FIL=Image.fromarray(np.uint8(self.filter_array),mode='L')
        # self.fitler_FIL = ImageEnhance.Brightness(self.fitler_FIL)
        # brightness = 10
        # self.fitler_FIL = self.fitler_FIL.enhance(brightness)
        self.origin_FIL=Image.fromarray(self.origin_array,mode='L')
        self.oring_img=ImageQt.ImageQt(self.origin_FIL)
        self.filter_img=ImageQt.ImageQt(self.fitler_FIL)

        p2=gray2qimage(np.uint8(self.slices[self.index].pixel_array), normalize=(0, 255))
        self.oring_pixmap=QPixmap(QImage(self.oring_img))
        self.filter_pixmap=QPixmap(QImage(self.filter_img))
        self.label.setPixmap(self.oring_pixmap)
        self.label_2.setPixmap(self.filter_pixmap)

    def wheelEvent(self, event):
        max = 512
        min = 200
        print(self.index)
        if not self.ctrlPressed:
            if event.angleDelta().y() >= 120:
                # 滚动3%
                # new = self.label.width() + max * 0.03
                # if new > max:
                # self.emit(self.slideMoved, new)
                self.index+=1
                if self.index>=self.maxslice-1:
                    self.index=self.maxslice-1
            elif event.angleDelta().y() <= -120:
                # new = self.label.width() - max * 0.03
                # new = self.label.width() - max * 0.03
                # if new < min:
                #     new = min
                self.index-=1
                if self.index<=0:
                    self.index=0
        else:
            if event.angleDelta().y() >= 120:
                self.scale=self.scale*1.03
            elif event.angleDelta().y() <= -120:
                self.scale=self.scale*0.95

        self.refrehdata()
        self.display()

    def keyReleaseEvent(self, QKeyEvent):
        if QKeyEvent.key()==QtCore.Qt.Key_Control:
            self.ctrlPressed=False
        return super().keyReleaseEvent(QKeyEvent)
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key()==QtCore.Qt.Key_Control:
            self.ctrlPressed=True
            print("The ctrl key is holding down")
        return super().keyPressEvent(QKeyEvent)


    def slot1(self):
        self.filter=self.comboBox.currentText()
        if self.filter=='阈值分割':
            self.threshold_slider.setEnabled(True)
        else:
            self.threshold_slider.setEnabled(False)
        self.refrehdata()
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
    # temp=slices[0].pixel_array
    # for i in range(1,len(list(slices))):
    #     temp=np.concatenate((temp,slices[i].pixel_array),axis=0)
    #
    # return temp.transpose(1,0,2)

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
    sys.exit(app.exec_())
