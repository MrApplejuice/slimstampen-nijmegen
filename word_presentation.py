import random

from model import *

from psychopy.core import getTime

class ApplicationInterface(object):
  def learn(self, image, word, translation):
    raise NotImplementedError()
  def test(self, word, answerToDisplay, imageAnswer):
    raise NotImplementedError()
  def displayCorrect(self, typedWord, correctAnswer):
    raise NotImplementedError()
  def displayWrong(self, typedWord, correctAnswer, image):
    raise NotImplementedError()
  def mixedup(self, leftUpper, leftLower, rightUpper, rightLower):
    raise NotImplementedError()
  def updateHighscore(self, score):
    raise NotImplementedError()

class AssignmentModel(object):
  def __init__(self, appInterface, stimuli):
    self.__appInterface = appInterface
    
    def makeWordItem(wordDict):
      wi = WordItem(s["word"].strip().lower())
      wi.translation = s["translation"].strip().lower()
      wi.image = s["image"].strip()
      return wi
    
    self.__stimuli = [makeWordItem(s) for s in stimuli]
    
    self.currentScore = 0
    
  def findMixedUpWord(self, typedWord):
    typedWord = typedWord.lower().strip()
    for s in self.__stimuli:
      if s.presentations:
        if typedWord == s.translation:
          return s
    return None
    
  def run(self):
    mainTimer = getTime
    
    learnSequence = list(self.__stimuli)
    random.shuffle(learnSequence)
    
    for stimulus in learnSequence:
      newPresentation = WordItemPresentation()
      newPresentation.decay = calculateNewDecay(stimulus, mainTimer())

      self.__appInterface.learn(stimulus.image, stimulus.name, stimulus.translation)
      
      newPresentation.time = mainTimer()
      stimulus.presentations.append(newPresentation)
      
    for x in xrange(20):
      predictionTime = mainTimer() + 15
      minActivationStimulus = min([(calculateActivation(s, predictionTime), s) for s in learnSequence], key=lambda x: x[0])[1]
      print [(calculateActivation(s, predictionTime), s.name, s.alpha) for s in learnSequence]
      print calculateActivation(minActivationStimulus, predictionTime), minActivationStimulus.name
      
      stimulus = minActivationStimulus
      

      newPresentation = WordItemPresentation()
      presentationStartTime = mainTimer()
      newPresentation.decay = calculateNewDecay(stimulus, presentationStartTime)

      response = self.__appInterface.test(stimulus.name)
      
      if response.lower() == stimulus.translation.lower():
        self.currentScore += 10
        self.__appInterface.updateHighscore(self.currentScore)
        self.__appInterface.displayCorrect(response, stimulus.translation)
        repeat = False
      else:
        stimulus.alpha += 0.02
        newPresentation.decay = calculateNewDecay(stimulus, presentationStartTime)
        
        mixedUpWord = self.findMixedUpWord(response)
        if mixedUpWord:
          self.__appInterface.mixedup(stimulus.name, stimulus.translation, mixedUpWord.name, mixedUpWord.translation)
        else:
          self.__appInterface.displayWrong(response, stimulus.translation, stimulus.image)

      newPresentation.time = mainTimer()
      stimulus.presentations.append(newPresentation)
