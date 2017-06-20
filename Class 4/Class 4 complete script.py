# -*- coding: utf-8 -*-
"""
Class # 4  -  Exercise
"""
import vtk

rectGridReader = vtk.vtkRectilinearGridReader()
rectGridReader.SetFileName("../data/jet4_0.500.vtk")
rectGridReader.Update()

#------------ Grid Outline and Grid Rectilinear Geometry Filters
rectGridOutline = vtk.vtkRectilinearGridOutlineFilter()
rectGridOutline.SetInputData(rectGridReader.GetOutput())

plane = vtk.vtkRectilinearGridGeometryFilter()
plane.SetInputData(rectGridReader.GetOutput())
plane.SetExtent(0, 128, 0, 0, 0, 128) #sets dimensions in each axis

rectGridOutlineMapper = vtk.vtkPolyDataMapper()
rectGridOutlineMapper.SetInputConnection(rectGridOutline.GetOutputPort())

rectGridGeomMapper = vtk.vtkPolyDataMapper()
rectGridGeomMapper.SetInputConnection(plane.GetOutputPort())

outlineActor = vtk.vtkActor()
outlineActor.SetMapper(rectGridOutlineMapper)
outlineActor.GetProperty().SetColor(0, 0, 0)

gridGeomActor = vtk.vtkActor()
gridGeomActor.SetMapper(rectGridGeomMapper)
gridGeomActor.GetProperty().SetRepresentationToWireframe()
gridGeomActor.GetProperty().SetColor(1, 0, 0)

#-------------- vtkCalculator
magnitudeCalcFilter = vtk.vtkArrayCalculator()
magnitudeCalcFilter.SetInputConnection(rectGridReader.GetOutputPort())
magnitudeCalcFilter.AddVectorArrayName('vectors')
# Set up here the array that is going to be used for the computation ('vectors')
magnitudeCalcFilter.SetResultArrayName('magnitude')
magnitudeCalcFilter.SetFunction("mag(vectors)")
# Set up here the function that calculates the magnitude of a vector
magnitudeCalcFilter.Update()

#-------------- Point filter
#Extract the data from the result of the vtkCalculator
points = vtk.vtkPoints()
grid = magnitudeCalcFilter.GetOutput()
grid.GetPoints(points)
scalars = grid.GetPointData().GetArray('magnitude')

#Create an unstructured grid that will contain the points and scalars data
ugrid = vtk.vtkUnstructuredGrid()
ugrid.SetPoints(points)
ugrid.GetPointData().SetScalars(scalars)

#Populate the cells in the unstructured grid using the output of the vtkCalculator
for i in range (0, grid.GetNumberOfCells()):
    cell = grid.GetCell(i)
    ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
    
#There are too many points, let's filter the points
subset = vtk.vtkMaskPoints()
subset.SetOnRatio(60)
subset.RandomModeOn()
subset.SetInputData(ugrid)

#Make a vtkPolyData with a vertex on each point.
pointsGlyph = vtk.vtkVertexGlyphFilter()
pointsGlyph.SetInputConnection(subset.GetOutputPort())
#pointsGlyph.SetInputData(ugrid)
pointsGlyph.Update()

pointsMapper = vtk.vtkPolyDataMapper()
pointsMapper.SetInputConnection(pointsGlyph.GetOutputPort())
pointsMapper.SetScalarModeToUsePointData()

pointsActor = vtk.vtkActor()
pointsActor.SetMapper(pointsMapper)

#-------------- Isosurfaces filter
scalarRange = ugrid.GetPointData().GetScalars().GetRange()
lut = vtk.vtkLookupTable()
lut.SetNumberOfColors(256)
lut.SetHueRange(0.667, 0.0)
lut.SetVectorModeToMagnitude()
lut.Build()
isoFilter = vtk.vtkContourFilter()
isoFilter.SetInputData(ugrid)
isoFilter.GenerateValues(10, scalarRange)

isoMapper = vtk.vtkPolyDataMapper()
isoMapper.SetInputConnection(isoFilter.GetOutputPort())
isoMapper.SetLookupTable(lut)

isoActor = vtk.vtkActor()
isoActor.SetMapper(isoMapper)
isoActor.GetProperty().SetOpacity(0.5)

#-------------- Hedgehog Filter
subset = vtk.vtkMaskPoints()
subset.SetOnRatio(5)
subset.RandomModeOn()
subset.SetInputConnection(rectGridReader.GetOutputPort())

lut = vtk.vtkLookupTable()
lut.SetNumberOfColors(256)
lut.SetHueRange(0.667, 0.0)
lut.SetVectorModeToMagnitude()
lut.Build()

hh = vtk.vtkHedgeHog()
hh.SetInputConnection(subset.GetOutputPort())
hh.SetScaleFactor(0.001)

hhm = vtk.vtkPolyDataMapper()
hhm.SetInputConnection(hh.GetOutputPort())
hhm.SetLookupTable(lut)
hhm.SetScalarVisibility(True)
hhm.SetScalarModeToUsePointFieldData()
hhm.SelectColorArray('vectors')
hhm.SetScalarRange((rectGridReader.GetOutput().GetPointData().GetVectors().GetRange(-1)))

hedgeActor = vtk.vtkActor()
hedgeActor.SetMapper(hhm)

#-------------- Rendering
renderer = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(renderer)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

#------- Un-Comment any actor you want to visualize
renderer.AddActor(gridGeomActor)
renderer.AddActor(outlineActor)
renderer.AddActor(hedgeActor)
renderer.AddActor(isoActor)
renderer.AddActor(pointsActor)

renderer.SetBackground(1, 1, 1)
 
renWin.SetSize(800, 800)
 
# interact with data
renWin.Render()
iren.Start()