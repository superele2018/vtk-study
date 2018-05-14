import vtk,scipy,os,readdicom
import numpy as np
from vtk import *
from scipy import ndimage as ndi

def load_scan(path):
    slices = [readdicom.read_file(path + '/' + s) for s in os.listdir(path)]
    slices.sort(key = lambda x: int(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices


def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)
    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0
    # Convert to Hounsfield units (HU)
    for slice_number in range(len(slices)):
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope
        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
        image[slice_number] += np.int16(intercept)
    return np.array(image, dtype=np.int16)

def resample(image, scan, new_spacing=[1,1,1]):
    # Determine current pixel spacing
    spacing = map(float, ([scan[0].SliceThickness] + scan[0].PixelSpacing))
    spacing = np.array(list(spacing))
    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor
    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor, mode='nearest')
    return image, new_spacing



if __name__ == '__main__':

    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName("D:\Anaconda\workspace\pytest\patient")
    reader.SetDataByteOrderToLittleEndian()

    first_patient=load_scan('D:\Anaconda\workspace\pytest\patient')
    first_patient_pixels=get_pixels_hu(first_patient)
    # pix_resampled, spacing = resample(first_patient_pixels, first_patient, [1, 1, 1])
    # id = vtk.vtkImageData()
    # id.SetDimensions(pix_resampled.shape[0], pix_resampled.shape[1], pix_resampled.shape[2])
    # if vtk.VTK_MAJOR_VERSION <= 5:
    #     id.SetNumberOfScalarComponents(1)
    #     id.SetScalarTypeToDouble()
    # else:
    #     id.AllocateScalars(vtk.VTK_DOUBLE, 1)
    # for x in range(0,pix_resampled.shape[0]):
    #     for y in range(0,pix_resampled.shape[1]):
    #         for z in range(0,pix_resampled.shape[2]):
    #             id.SetScalarComponentFromFloat(x,y,z,0,float(pix_resampled[x,y,z]))
    # id.SetOrigin(0.0, 0.0, 0.0)
    #
    # writer = vtk.vtkXMLImageDataWriter()
    # writer.SetFileName('writeImageData.vti')
    # if vtk.VTK_MAJOR_VERSION <= 5:
    #     writer.SetInputConnection(id.GetProducerPort())
    # else:
    #     writer.SetInputData(id)
    # writer.Write()
    #
    # reader = vtk.vtkXMLImageDataReader()
    # reader.SetFileName('writeImageData.vti')
    # reader.Update()
    threshould = vtk.vtkImageThreshold()
    threshould.SetInputConnection(reader.GetOutputPort())
    threshould.ThresholdByUpper(1)
    threshould.SetInValue(255)
    threshould.SetOutValue(0)
    threshould.Update()

    readerImageCast =  vtk.vtkImageCast()
    readerImageCast.SetInputConnection(threshould.GetOutputPort())
    readerImageCast.SetOutputScalarTypeToFloat()
    readerImageCast.Update()

    opactiyTransferFunction = vtk.vtkPiecewiseFunction ()
    opactiyTransferFunction.AddPoint(120, 0.0)
    opactiyTransferFunction.AddPoint(250, 1.0)
    opactiyTransferFunction.AddPoint(520, 1.0)
    opactiyTransferFunction.AddPoint(650, 0.0)

    colorTransferFunction =   vtk.vtkColorTransferFunction ()
    colorTransferFunction.AddRGBPoint(120, 255/255.0, 98/255.0, 98/255.0) # 255.0, 98 # 255.0, 98 # 255.0)
    colorTransferFunction.AddRGBPoint(250,  255/255.0, 255/255.0, 180/255.0) # 255.0, 255 # 255.0, 180 # 255.0)
    colorTransferFunction.AddRGBPoint(520, 1.0, 1.0, 1.0)
    colorTransferFunction.AddRGBPoint(650, 1.0, 1.0, 1.0)

    gradientTransferFunction =   vtk.vtkPiecewiseFunction ()
    gradientTransferFunction.AddPoint(120, 2.0)
    gradientTransferFunction.AddPoint(250, 2.0)
    gradientTransferFunction.AddPoint(520, 0.1)
    gradientTransferFunction.AddPoint(650, 0.1)

    volumeProperty =   vtk.vtkVolumeProperty ()
    volumeProperty.SetColor(colorTransferFunction)
    volumeProperty.SetScalarOpacity(opactiyTransferFunction)
    volumeProperty.SetGradientOpacity(gradientTransferFunction)
    volumeProperty.ShadeOn() ## 阴影
    ## volumeProperty.SetInterpolationTypeToLinear() ## 直线与样条插值之间逐发函数
    volumeProperty.SetAmbient(0.2) ## 环境光系数
    volumeProperty.SetDiffuse(0.9) ## 漫反射
    volumeProperty.SetSpecular(0.2) ## 高光系数
    volumeProperty.SetSpecularPower(10) ## 高光强度

    # compositeRaycastFunction = vtk.vtkVolumeRayCastCompositeFunction ()

    volumeMapper = vtk.vtkGPUVolumeRayCastMapper ()
    # volumeMapper.SetVolumeRayCastFunction(compositeRaycastFunction) ## 载入体绘制方法
    volumeMapper.SetInputConnection(readerImageCast.GetOutputPort())
    # *fixedPointVolumeMapper = ixedPointVolumeRayCastMapper()
    # fixedPointVolumeMapper.SetInput(dicomImagereader.GetOutput()) * #

    volume =  vtk.vtkVolume ()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty) ## 设置体属性

    ren1 =   vtk.vtkRenderer ()
    ren1.AddVolume(volume)
    ren1.SetBackground(1, 1, 1)

    renWin =   vtk.vtkRenderWindow ()
    renWin.AddRenderer(ren1)
    renWin.SetSize(800, 800)

    iren =   vtk.vtkRenderWindowInteractor ()
    iren.SetRenderWindow(renWin)

    renWin.Render()
    iren.Start()