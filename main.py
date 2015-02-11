import sys

from visual import MovieVisualizer
from word_presentation import *

from dict_csv_serializer import CSVDictList

import psychopy.core as core
import psychopy.visual as visual

class MovieViewer(object):
  def __init__(self, win):
    self.__win = win
    self.__visualizer = None
    
  def playMovie(self, filename):
    if self.__visualizer is None:
      self.__visualizer = MovieVisualizer(self.__win, filename, (0, 0), 1.0)
    self.__visualizer.restart(filename)
    
    while self.__visualizer.stillRunning:
      self.__visualizer.draw()
      self.__win.flip()

class LearnWordViewer(object):
  def __init__(self, win):
    self.__win = win
    
    self.imageComponent = visual.ImageStim(win, pos=(0, -0.5), size=0.2)
    self.wordText = visual.ImageStim(win, pos=(-.75, 0.2))
    self.translationText = visual.ImageStim(win, pos=( .75, 0.2))
    
  def show(self, image, word, translation):
    self.imageComponent.image = image
    self.wordText.text = word
    self.translationText.text = translation
    
    self.imageComponent.draw()
    self.wordText.draw()
    self.__win.flip()
    core.wait(5)
    
    self.imageComponent.draw()
    self.wordText.draw()
    self.translationText.draw()
    self.__win.flip()
    core.wait(5)
    

if __name__ == '__main__':
  if ("?" in sys.argv[1:]) or ("help" in sys.argv[1:]):
    print """
Usage:
  python main [windowed]
  
Parameter:
  fullscreen    Specify the parameter "fullscreen" to start the application in fullscreen mode
"""
  fullscreenMode = "windowed" in sys.argv[1:]
  
  print "Starting in", "fullscreen" if fullscreenMode else "window", "mode"
  
  mainWindow = visual.Window(fullscr=fullscreenMode, size=(1280, 720))

  # Load stimuli
  stimuli = CSVDictList()
  stimuli.load("testdata/test.csv")
  
  # Initialize different "scenes"
  movieViewer = MovieViewer(mainWindow)
  learnWordViewer = LearnWordViewer(mainWindow)
  
  #movieViewer.playMovie("/media/crepo/TEMP/Mnemonic_task/stimuli/MemrisePrizev3.wmv")
  
  class ThisAppInterface(ApplicationInterface):
    def learn(self, image, word, translation):
      learnWordViewer.show(image, word, translation)
  assignmentModel = AssignmentModel(ThisAppInterface(), stimuli)

  assignmentModel.run()
