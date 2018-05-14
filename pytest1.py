import sys
import vtk
from PyQt4 import QtCore, QtGui
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
import vtk.qvtk

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.frame = QtGui.QFrame()

        self.vl = QtGui.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Create source
        source = vtk.vtkDICOMImageReader()
        source.SetFileName("D:\Anaconda\workspace\pytest\patient\\1.dcm")

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.ren.AddActor(actor)

        self.ren.ResetCamera()

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.show()
        self.iren.Initialize()


def new(renderWindowInteractor):
    a=vtk.QVTKWidget()
    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName("D:\Anaconda\workspace\pytest\patient")
    # reader.SetDirectoryName("G:\Win64\Anaconda3.4\workplace\\vtk\dicom")
    reader.Update()
    imageViewer=vtk.vtkImageViewer2()
    imageViewer.SetInputConnection(reader.GetOutputPort())
    sliceTextProp = vtk.vtkTextProperty()
    sliceTextProp.SetFontFamilyToCourier()
    sliceTextProp.SetFontSize(20)
    sliceTextProp.SetVerticalJustificationToBottom()
    sliceTextProp.SetJustificationToLeft()

    sliceTextMapper =vtk.vtkTextMapper()
    msg = str(imageViewer.GetSliceMin())+'/'+ str(imageViewer.GetSliceMax())
    sliceTextMapper.SetInput(msg)
    sliceTextMapper.SetTextProperty(sliceTextProp)

    sliceTextActor = vtk.vtkActor2D()
    sliceTextActor.SetMapper(sliceTextMapper)
    sliceTextActor.SetPosition(15, 10)

    usageTextProp = vtk.vtkTextProperty()
    usageTextProp.SetFontFamilyToCourier()
    usageTextProp.SetFontSize(14)
    usageTextProp.SetVerticalJustificationToTop()
    usageTextProp.SetJustificationToLeft()

    usageTextMapper = vtk.vtkTextMapper()
    usageTextMapper.SetInput(
        "- Slice with mouse wheel\n  or Up/Down-Key\n- Zoom with pressed right\n  mouse button while dragging")
    usageTextMapper.SetTextProperty(usageTextProp)

    usageTextActor = vtk.vtkActor2D()
    usageTextActor.SetMapper(usageTextMapper)
    usageTextActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    usageTextActor.GetPositionCoordinate().SetValue(0.05, 0.95)

    # renderWindowInteractor =vtk.vtkRenderWindowInteractor()

    # myInteractorStyle = vtk. myVtkInteractorStyleImage()
    #
    # myInteractorStyle.SetImageViewer(imageViewer)
    # myInteractorStyle.SetStatusMapper(sliceTextMapper)

    imageViewer.SetupInteractor(renderWindowInteractor)
    imageViewer.SetSlice(12)
    # style= vtk.vtkInteractorStyleUser(imageViewer=imageViewer)
    # renderWindowInteractor.SetInteractorStyle(style)
    imageViewer.GetRenderer().AddActor2D(sliceTextActor)
    imageViewer.GetRenderer().AddActor2D(usageTextActor)
    imageViewer.Render()
    imageViewer.GetRenderer().ResetCamera()
    imageViewer.Render()
    # renderWindowInteractor.Initialize()
    # renderWindowInteractor.Start()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())