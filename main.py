#!/usr/bin/python

import sys

from visual import MovieVisualizer
from word_presentation import *
from editing import recordKeyboardInputs

from dict_csv_serializer import CSVDictList

import psychopy.core as core
import psychopy.visual as visual

def determineTextWidth(fontStimulus):
  # Determine text width using psychopy's pyglet infrastructure
  glyphList = fontStimulus._font.get_glyphs(fontStimulus.text)
  thisPixWidth = sum([0] + [x.advance for x in glyphList])
  return thisPixWidth * fontStimulus.height / fontStimulus._fontHeightPix / 1.5

def setLineStrikethrough(textStim, lineStim):
  lineStim.start = (textStim.pos[0], textStim.pos[1] - 0.01)
  lineStim.end = (textStim.pos[0] + determineTextWidth(textStim), textStim.pos[1] - 0.01)


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
    
  def _prepareImage(self, image):
    self.imageComponent.size = None
    self.imageComponent.image = image
    self.imageComponent.size *= self.IMAGE_SIZE / self.imageComponent.size[1]
    
  def show(self, image, word, translation):
    WAIT_TIMES = [15.0, 15.0] # maximum presentation times before program automatically continues, , PP can move on self-paced earlier
    ANIMATION_TIME = 0.01
    
    TEXT_HEIGHT = 0.1

    self._prepareImage(image)    

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

    self.translationText.height = TEXT_HEIGHT
    self.__win.flip()
    recordKeyboardInputs(self.__win, None, countdown=core.CountdownTimer(WAIT_TIMES[1] - ANIMATION_TIME))

    self.wordText.autoDraw = False
    self.translationText.autoDraw = False
    self.imageComponent.autoDraw = False
    
class TestWordViewer(LearnWordViewer):
  UPPER_TEXT_POS = LearnWordViewer.UPPER_TEXT_POS
  LOWER_TEXT_POS = LearnWordViewer.LOWER_TEXT_POS

  ANIMATION_TIME = 0.1
  TEXT_HEIGHT = 0.1

  def __init__(self, win):
    super(TestWordViewer, self).__init__(win)
    
    self.__win = win
    
    self.wordText = visual.TextStim(win, pos=self.UPPER_TEXT_POS, alignHoriz='left')
    self.typedText = visual.TextStim(win, pos=self.LOWER_TEXT_POS, alignHoriz='left')
    self.correctAnswer = visual.TextStim(win, pos=self.LOWER_TEXT_POS, alignHoriz='left', color=(0, 1, 0))
    self.strikeThroughLine = visual.Line(win, lineColor=(1, 0, 0), lineWidth=10)
    
  def test(self, word):
    self.typedText.color = (1, 1, 1)

    self.wordText.text = word
    self.wordText.autoDraw = True
    
    # Animate text popup
    currentHeight = 0.0
    startTime = core.getTime()
    now = core.getTime()
    while now - startTime < self.ANIMATION_TIME:
      currentHeight = self.TEXT_HEIGHT * (now - startTime) / self.ANIMATION_TIME
      self.wordText.height = currentHeight
      self.__win.flip()
      now = core.getTime()

    self.wordText.height = self.TEXT_HEIGHT
    self.__win.flip()
    
    self.typedText.height = self.TEXT_HEIGHT
    self.typedText.autoDraw = True
    
    typedWord = None
    while not typedWord:    
      history = recordKeyboardInputs(self.__win, self.typedText)
      typedWord = None if len(history) == 0 else history[-1]["current_text"].strip()

    self.wordText.autoDraw = False
    self.typedText.autoDraw = False

    return typedWord
    
  def showCorrect(self):
    self.wordText.autoDraw = True
    self.typedText.autoDraw = True
    
    self.typedText.color = (0, 1, 0)
    recordKeyboardInputs(self.__win, None, countdown=core.CountdownTimer(1))

    self.wordText.autoDraw = False
    self.typedText.autoDraw = False

  def showStrikthroughLine(self):
    self.typedText.color = (1, 0, 0)

    self.typedText.draw()
    setLineStrikethrough(self.typedText, self.strikeThroughLine)
    self.strikeThroughLine.autoDraw = True

  def showWrong(self, answerToDisplay, image):
    self.wordText.autoDraw = True
    self.typedText.autoDraw = True
    
    self._prepareImage(image)

    if not self.typedText.text:
      self.typedText.text = "x"
    
    self.showStrikthroughLine()

    self.correctAnswer.text = answerToDisplay
    self.correctAnswer.pos = (self.strikeThroughLine.end[0] + 0.02, self.typedText.pos[1])
    
    self.correctAnswer.autoDraw = True
    self.imageComponent.autoDraw = True
    
    currentHeight = 0.0
    startTime = core.getTime()
    now = core.getTime()
    while now - startTime < self.ANIMATION_TIME:
      currentHeight = self.TEXT_HEIGHT * (now - startTime) / self.ANIMATION_TIME
      self.correctAnswer.height = currentHeight
      self.__win.flip()
      now = core.getTime()
    self.correctAnswer.height = self.TEXT_HEIGHT
    self.__win.flip()
    core.wait(1 - self.ANIMATION_TIME)
    recordKeyboardInputs(self.__win, None, countdown=core.CountdownTimer(10))

    self.imageComponent.autoDraw = False
    self.correctAnswer.autoDraw = False
    self.strikeThroughLine.autoDraw = False
    self.wordText.autoDraw = False
    self.typedText.autoDraw = False

class MixedUpViewer(object):
  UPPER_TEXT_POSITIONS = [LearnWordViewer.UPPER_TEXT_POS, (-LearnWordViewer.UPPER_TEXT_POS[0], LearnWordViewer.UPPER_TEXT_POS[1])]
  LOWER_TEXT_POSITIONS = [LearnWordViewer.LOWER_TEXT_POS, (-LearnWordViewer.LOWER_TEXT_POS[0], LearnWordViewer.LOWER_TEXT_POS[1])]

  TEXT_HEIGHT = 0.1

  def __init__(self, win, testScreen):
    self.__win = win
    
    self.mixedUpText = visual.TextStim(win, pos=(self.UPPER_TEXT_POSITIONS[0][0], 0), alignHoriz='left', text="You mixed up two words:", height=self.TEXT_HEIGHT)
    self.upperTexts = [testScreen.wordText,  visual.TextStim(win, pos=self.UPPER_TEXT_POSITIONS[1], alignHoriz='left')]
    self.lowerTexts = [testScreen.typedText, visual.TextStim(win, pos=self.LOWER_TEXT_POSITIONS[1], alignHoriz='left')]
    self.strikeThroughLine = testScreen.strikeThroughLine
    
    self.showStrikethroughLine = testScreen.showStrikthroughLine
    
  def show(self, leftUpper, leftLower, rightUpper, rightLower):
    TEXT_HEIGHT = self.TEXT_HEIGHT
    
    ANIMATION_TIME = 0.2
    FORCED_WAIT = 1
    TOTAL_WAIT = 10
    
    self.upperTexts[0].autoDraw = True
    self.lowerTexts[0].autoDraw = True
    self.showStrikethroughLine()
    self.mixedUpText.autoDraw = True
    self.__win.flip()
    core.wait(1)

    self.upperTexts[0].text = leftUpper
    self.upperTexts[1].text = rightUpper
    self.lowerTexts[0].text = leftLower
    self.lowerTexts[1].text = rightLower

    for t in self.upperTexts + self.lowerTexts:
      t.color = (1, 1, 1)
      t.autoDraw = True
    self.strikeThroughLine.autoDraw = False
      
    currentHeight = 0.0
    startTime = core.getTime()
    now = core.getTime()
    while now - startTime < ANIMATION_TIME:
      currentHeight = TEXT_HEIGHT * (now - startTime) / ANIMATION_TIME;
      for t in self.upperTexts + self.lowerTexts:
        if t != self.upperTexts[0]: # Do not animate upper left word
          t.height = currentHeight
      self.__win.flip()
      now = core.getTime()
    for t in self.upperTexts + self.lowerTexts:
      t.height = TEXT_HEIGHT
    self.__win.flip()
    
    core.wait(FORCED_WAIT - ANIMATION_TIME)
    
    recordKeyboardInputs(self.__win, None, countdown=core.CountdownTimer(TOTAL_WAIT - FORCED_WAIT))

    for t in self.upperTexts + self.lowerTexts:
      t.autoDraw = False
    self.mixedUpText.autoDraw = False

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
    mixedupViewer = MixedUpViewer(mainWindow, testWordViewer)
    
    #movieViewer.playMovie("/media/crepo/TEMP/Mnemonic_task/stimuli/MemrisePrizev3.wmv")
    
    class ThisAppInterface(ApplicationInterface):
      def learn(self, *args):
        learnWordViewer.show(*args)
      def test(self, *args):
        return testWordViewer.test(*args)
      def updateHighscore(self, *args):
        highscoreHighscoreViewer.updateHighscore(*args)
      def mixedup(self, *args):
        mixedupViewer.show(*args)
      def displayCorrect(self, typedWord, correctWord):
        testWordViewer.showCorrect()
      def displayWrong(self, typedWord, correctWord, image):
        testWordViewer.showWrong(correctWord, image)
        
    assignmentModel = AssignmentModel(ThisAppInterface(), stimuli)

    assignmentModel.run()
