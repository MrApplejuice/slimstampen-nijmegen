import sys

from visual import MovieVisualizer
from word_presentation import *
from editing import recordKeyboardInputs

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
    
    self.imageComponent = visual.ImageStim(win, pos=(0, 0.5), size=0.5)
    self.wordText = visual.TextStim(win, pos=(-.25, -0.2))
    self.translationText = visual.TextStim(win, pos=( .25, -0.2))
    
  def show(self, image, word, translation):
    TOTAL_WAIT = 3.0
    ANIMATION_TIME = 0.25
    
    TEXT_HEIGHT = 0.1
    
    self.imageComponent.image = image
    self.wordText.text = word
    self.translationText.text = translation
    
    self.imageComponent.autoDraw = True
    self.wordText.autoDraw = True
    
    # Animate text popup
    currentHeight = 0.0
    startTime = core.getTime()
    now = core.getTime()
    while now - startTime < ANIMATION_TIME:
      currentHeight = TEXT_HEIGHT * (now - startTime) / ANIMATION_TIME;
      self.wordText.height = currentHeight
      self.__win.flip()
      now = core.getTime()

    self.wordText.height = TEXT_HEIGHT
    self.__win.flip()
    core.wait(TOTAL_WAIT - ANIMATION_TIME)
    
    self.translationText.autoDraw = True

    currentHeight = 0.0
    startTime = core.getTime()
    now = core.getTime()
    while now - startTime < ANIMATION_TIME:
      currentHeight = TEXT_HEIGHT * (now - startTime) / ANIMATION_TIME;
      self.translationText.height = currentHeight
      self.__win.flip()
      now = core.getTime()

    self.__win.flip()
    core.wait(TOTAL_WAIT - ANIMATION_TIME)

    self.wordText.autoDraw = False
    self.translationText.autoDraw = False
    self.imageComponent.autoDraw = False
    
class TestWordViewer(object):
  def __init__(self, win):
    self.__win = win
    
    self.wordText = visual.TextStim(win, pos=(-.25, -0.2))
    self.typedText = visual.TextStim(win, pos=( .25, -0.2))
    
  def test(self, word):
    ANIMATION_TIME = 0.25
    
    TEXT_HEIGHT = 0.1
    
    self.wordText.text = word
    
    self.wordText.autoDraw = True
    
    # Animate text popup
    currentHeight = 0.0
    startTime = core.getTime()
    now = core.getTime()
    while now - startTime < ANIMATION_TIME:
      currentHeight = TEXT_HEIGHT * (now - startTime) / ANIMATION_TIME;
      self.wordText.height = currentHeight
      self.__win.flip()
      now = core.getTime()

    self.wordText.height = TEXT_HEIGHT
    self.__win.flip()
    
    self.typedText.autoDraw = True
    
    history = recordKeyboardInputs(self.__win, self.typedText)
    self.wordText.autoDraw = False
    self.typedText.autoDraw = False
    
    return "" if len(history) == 0 else history[-1]["current_text"]

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
  testWordViewer = TestWordViewer(mainWindow)
  
  #movieViewer.playMovie("/media/crepo/TEMP/Mnemonic_task/stimuli/MemrisePrizev3.wmv")
  
  class ThisAppInterface(ApplicationInterface):
    def learn(self, image, word, translation):
      learnWordViewer.show(image, word, translation)
    def test(self, word):
      return testWordViewer.test(word)
      
  assignmentModel = AssignmentModel(ThisAppInterface(), stimuli)

  assignmentModel.run()
