import vtk


if __name__ == '__main__':


    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName("D:\Anaconda\workspace\pytest\patient")
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

    renderWindowInteractor =vtk.vtkRenderWindowInteractor()

    # myInteractorStyle = vtk. myVtkInteractorStyleImage()
    #
    # myInteractorStyle.SetImageViewer(imageViewer)
    # myInteractorStyle.SetStatusMapper(sliceTextMapper)

    imageViewer.SetupInteractor(renderWindowInteractor)
    imageViewer.SetSlice(12)
    style= vtk.vtkInteractorStyleUser()
    renderWindowInteractor.SetInteractorStyle(style)
    imageViewer.GetRenderer().AddActor2D(sliceTextActor)
    imageViewer.GetRenderer().AddActor2D(usageTextActor)
    imageViewer.Render()
    imageViewer.GetRenderer().ResetCamera()
    imageViewer.Render()
    renderWindowInteractor.Initialize()
    renderWindowInteractor.Start()
