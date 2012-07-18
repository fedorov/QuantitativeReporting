import os
import string
from __main__ import vtk, qt, ctk, slicer
from DICOMLib import DICOMPlugin
from DICOMLib import DICOMLoadable

#
# This is the plugin to handle translation of DICOM objects
# that can be represented as multivolume objects
# from DICOM files into MRML nodes.  It follows the DICOM module's
# plugin architecture.
#

class DICOMSegmentationPluginClass(DICOMPlugin):

  def __init__(self,epsilon=0.01):
    super(DICOMSegmentationPluginClass,self).__init__()
    self.loadType = "DICOMSegmentation"

  def examine(self,fileLists):
    """ Returns a list of DICOMLoadable instances
    corresponding to ways of interpreting the 
    fileLists parameter.
    """
    loadables = []
    for files in fileLists:
      loadables += self.examineFiles(files)
    return loadables

  def examineFiles(self,files):

    print("DICOMSegmentationPlugin::examine")

    """ Returns a list of DICOMLoadable instances
    corresponding to ways of interpreting the 
    files parameter.
    """
    loadables = []

    # just read the modality type; need to go to reporting logic, since DCMTK
    #   is not wrapped ...

    for file in files:

      print 'DICOM SEG plugin is parsing file ', file
      slicer.dicomDatabase.loadFileHeader(file)
      uid = slicer.dicomDatabase.headerValue("0008,0018") # SOPInstanceUID
      print 'Unparsed uid:', uid
      try:
        uid = uid[uid.index('[')+1:uid.index(']')]
      except ValueError:
        return []

      print 'DICOM SEG UID = ', uid

      d = slicer.dicomDatabase.headerValue("0008,103e") # SeriesDescription

      try:
        name = d[d.index('[')+1:d.index(']')]
      except ValueError:
        name = "Unknown"

      d = slicer.dicomDatabase.headerValue("0020,0011")
      try:
        num = d[d.index('[')+1:d.index(']')]
        name = num + ": " + name
      except ValueError:
        return []

      reportingLogic = None
      try:
        reportingLogic = slicer.modules.reporting.logic()
      except AttributeError:
        return []

      isDicomSeg = reportingLogic.IsDicomSeg(file)

      if isDicomSeg:
        loadable = DICOMLib.DICOMLoadable()
        loadable.files = file
        loadable.name = name + ' - as a DICOM SEG object'
        loadable.tooltip = loadable.name
        loadable.selected = True
        loadable.uid = uid
        loadables.append(loadable)
        print('DICOM SEG modality found')

    return loadables

  def load(self,loadable):
    """ Call Reporting logic to load the DICOM SEG object
    """
    print('DICOM SEG load()')
    labelNodes = vtk.vtkCollection()

    uid = None

    try:
      reportingLogic = slicer.modules.reporting.logic()
      uid = loadable.uid
      print 'in load(): uid = ', uid
    except AttributeError:
      return False

    res = False
    # default color node will be used
    res = reportingLogic.DicomSegRead(labelNodes, uid)
    print 'Read this many labels:',labelNodes.GetNumberOfItems()

    defaultColorNode = reportingLogic.GetDefaultColorNode()
    for i in range(labelNodes.GetNumberOfItems()):
      # create and initialize the display node to use default color node
      displayNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLScalarVolumeDisplayNode')
      displayNode.SetReferenceCount(displayNode.GetReferenceCount()-1)
      displayNode.SetAndObserveColorNodeID(defaultColorNode.GetID())
      slicer.mrmlScene.AddNode(displayNode)

      # assign it to the label node
      # this is done here as opposed to Reporting logic to minimize the
      # dependencies of the DICOM SEG functionality in the Slicer internals
      labelNode = labelNodes.GetItemAsObject(i)
      labelNode.SetAndObserveDisplayNodeID(displayNode.GetID())
      slicer.mrmlScene.AddNode(labelNode)

    return True

#
# DICOMSegmentationPlugin
#

class DICOMSegmentationPlugin:
  """
  This class is the 'hook' for slicer to detect and recognize the plugin
  as a loadable scripted module
  """
  def __init__(self, parent):
    parent.title = "DICOM Segmentation Object Import Plugin"
    parent.categories = ["Developer Tools.DICOM Plugins"]
    parent.contributors = ["Andrey Fedorov, BWH"]
    parent.helpText = """
    Plugin to the DICOM Module to parse and load DICOM SEG modality.
    No module interface here, only in the DICOM module
    """
    parent.dependencies = ['Reporting', 'DICOM', 'Colors']
    parent.acknowledgementText = """
    This DICOM Plugin was developed by 
    Andrey Fedorov, BWH.
    and was partially funded by NIH grant U01CA151261.
    """

    # don't show this module - it only appears in the DICOM module
    parent.hidden = True

    # Add this extension to the DICOM module's list for discovery when the module
    # is created.  Since this module may be discovered before DICOM itself,
    # create the list if it doesn't already exist.
    try:
      slicer.modules.dicomPlugins
    except AttributeError:
      slicer.modules.dicomPlugins = {}
    slicer.modules.dicomPlugins['DICOMSegmentationPlugin'] = DICOMSegmentationPluginClass

#
#

class DICOMSegmentationPluginWidget:
  def __init__(self, parent = None):
    self.parent = parent
    
  def setup(self):
    # don't display anything for this widget - it will be hidden anyway
    pass

  def enter(self):
    pass
    
  def exit(self):
    pass
