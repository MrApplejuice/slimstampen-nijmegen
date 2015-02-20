#!/usr/bin/python

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
  UPPER_TEXT_POS = (-0.25, -0.56)
  LOWER_TEXT_POS = (-0.25, -0.76)

  def __init__(self, win):
    self.__win = win
    
    self.IMAGE_SIZE = 1.3
    
    self.imageComponent = visual.ImageStim(win, pos=(0, 1 - (self.IMAGE_SIZE / 2 + 0.05)))
    self.wordText = visual.TextStim(win, height=0.1, pos=self.UPPER_TEXT_POS, alignHoriz='left')
    self.translationText = visual.TextStim(win, height=0.1, pos=self.LOWER_TEXT_POS, alignHoriz='left')
    
  def show(self, image, word, translation):
    WAIT_TIMES = [15.0, 15.0]
    ANIMATION_TIME = 0.25
    
    TEXT_HEIGHT = 0.1
    
    self.imageComponent.size = None
    self.imageComponent.image = image
    self.imageComponent.size *= self.IMAGE_SIZE / self.imageComponent.size[1]

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
    recordKeyboardInputs(self.__win, None, countdown=core.CountdownTimer(WAIT_TIMES[0] - ANIMATION_TIME))
    
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
    recordKeyboardInputs(self.__win, None, countdown=core.CountdownTimer(WAIT_TIMES[1] - ANIMATION_TIME))

    self.wordText.autoDraw = False
    self.translationText.autoDraw = False
    self.imageComponent.autoDraw = False
    
class TestWordViewer(object):
  UPPER_TEXT_POS = LearnWordViewer.UPPER_TEXT_POS
  LOWER_TEXT_POS = LearnWordViewer.LOWER_TEXT_POS

  def __init__(self, win):
    self.__win = win
    
    self.wordText = visual.TextStim(win, pos=self.UPPER_TEXT_POS, alignHoriz='left')
    self.typedText = visual.TextStim(win, pos=self.LOWER_TEXT_POS, alignHoriz='left')
    self.correctAnswer = visual.TextStim(win, pos=self.LOWER_TEXT_POS, alignHoriz='left', color=(0, 1, 0))
    self.strikeThroughLine = visual.Line(win, lineColor=(1, 0, 0), lineWidth=10)
    
  def test(self, word, answerToDisplay, checkResponseFunction):
    ANIMATION_TIME = 0.1
    
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
    
    typedWord = None
    while not typedWord:    
      history = recordKeyboardInputs(self.__win, self.typedText)
      typedWord = None if len(history) == 0 else history[-1]["current_text"].strip()

    response = checkResponseFunction(typedWord)
    if response != ApplicationInterface.Response.NONE:
      if response == ApplicationInterface.Response.CORRECT:
        self.typedText.color = (0, 1, 0)
        recordKeyboardInputs(self.__win, None, countdown=core.CountdownTimer(1))
      elif response == ApplicationInterface.Response.WRONG:
        if not self.typedText.text:
          self.typedText.text = "x"
        
        self.typedText.color = (1, 0, 0)

        self.typedText.draw()

        # Determine text width using psychopy's pyglet infrastructure
        glyphList = self.typedText._font.get_glyphs(self.typedText.text)
        thisPixWidth = sum([0] + [x.advance for x in glyphList])
        thisTextWidth = thisPixWidth * self.typedText.height / self.typedText._fontHeightPix / 1.5
        
        self.strikeThroughLine.start = (self.typedText.pos[0], self.typedText.pos[1] - 0.01)
        self.strikeThroughLine.end = (self.typedText.pos[0] + thisTextWidth, self.typedText.pos[1] - 0.01)

        self.correctAnswer.text = answerToDisplay
        self.correctAnswer.pos = (self.strikeThroughLine.end[0] + 0.02, self.typedText.pos[1])
        
        self.correctAnswer.autoDraw = True
        self.strikeThroughLine.autoDraw = True
        
        currentHeight = 0.0
        startTime = core.getTime()
        now = core.getTime()
        while now - startTime < ANIMATION_TIME:
          currentHeight = TEXT_HEIGHT * (now - startTime) / ANIMATION_TIME;
          self.correctAnswer.height = currentHeight
          self.__win.flip()
          now = core.getTime()
        self.correctAnswer.height = TEXT_HEIGHT
        self.__win.flip()
        core.wait(1 - ANIMATION_TIME)
        recordKeyboardInputs(self.__win, None, countdown=core.CountdownTimer(10))

        self.correctAnswer.autoDraw = False
        self.strikeThroughLine.autoDraw = False
      else:
        raise ValueError("Wrong value returned by checkResponseFunction")
    self.typedText.color = (1, 1, 1)
    
    self.wordText.autoDraw = False
    self.typedText.autoDraw = False

    return typedWord

class HighscoreViewer(object):
  def __init__(self, win):
    self.__win = win
    
    self.__score = 0
    self.highscoreText = visual.TextStim(win, pos=(.7, -0.9), alignHoriz='left', height=0.05)
    self.updateHighscore(self.__score)
    self.highscoreText.autoDraw = True
    
  def updateHighscore(self, score):
    self.highscoreText.text = "Jouw score: {}".format(score)
  
if __name__ == '__main__':
  if ("?" in sys.argv[1:]) or ("help" in sys.argv[1:]):
    print """
Usage:
  python main [windowed]
  
Parameter:
  fullscreen    Specify the parameter "fullscreen" to start the application in fullscreen mode
"""
  else:
    fullscreenMode = "fullscreen" in sys.argv[1:]
    
    print "Starting in", "fullscreen" if fullscreenMode else "window", "mode"
    
    mainWindow = visual.Window(fullscr=fullscreenMode, size=(1280, 720))
    if mainWindow.winType != "pyglet":
      raise ValueError("Cannot only determine font widths for non-pyglet fonts")
    print "Main window uses backend: ", mainWindow.winType

    # Load stimuli
    stimuli = CSVDictList()
    stimuli.load("testdata/test.csv")
    
    # Initialize different "scenes"
    movieViewer = MovieViewer(mainWindow)
    learnWordViewer = LearnWordViewer(mainWindow)
    testWordViewer = TestWordViewer(mainWindow)
    highscoreHighscoreViewer = HighscoreViewer(mainWindow)
    
    #movieViewer.playMovie("/media/crepo/TEMP/Mnemonic_task/stimuli/MemrisePrizev3.wmv")
    
    class ThisAppInterface(ApplicationInterface):
      def learn(self, *args):
        learnWordViewer.show(*args)
      def test(self, *args):
        return testWordViewer.test(*args)
      def updateHighscore(self, *args):
        highscoreHighscoreViewer.updateHighscore(*args)
        
    assignmentModel = AssignmentModel(ThisAppInterface(), stimuli)

    assignmentModel.run()
