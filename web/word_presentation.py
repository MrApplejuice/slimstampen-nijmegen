import random

from model import *

TOTAL_TEST_DURATION = 57 * 60   # seconds
TEST_BLOCK_DURATION = 25 * 60  # seconds until this block is presented

ACTIVATION_PREDICTION_TIME_OFFSET = 15  # seconds
ACTIVATION_THRESHOLD_RETEST = -.8

ALPHA_ERROR_ADJUSTMENT_SUMMAND = 0.02

CORRECT_ANSWER_SCORE = 10

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
  def displayInstructions(self):
    raise NotImplementedError()
  def startInbetweenSession(self, imageWordPairs):
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

  @property
  def stimuliSummary(self):
      return [{
          "word": stimulus.name, 
          "translation": stimulus.translation, 
          "#presentations": len(stimulus.presentations),
          "alpha": stimulus.alpha
      } for stimulus in self.__stimuli]
    
  def run(self):
    mainTimer = getTime
    self.__appInterface.displayInstructions()

    totalTestTimer = CountdownTimer(TOTAL_TEST_DURATION)
    inbetweenSessionCountdown = CountdownTimer(TEST_BLOCK_DURATION)
    
    while totalTestTimer.getTime() > 0:
      presentedItems = filter(lambda x: len(x.presentations) > 0, self.__stimuli)
      
      stimulus = None
      minActivationStimulus = None
      if len(presentedItems) > 0:
        # Select item from presented items with activation <= ACTIVATION_THRESHOLD_RETEST
        predictionTime = mainTimer() + ACTIVATION_PREDICTION_TIME_OFFSET
        minActivation, minActivationStimulus = min([(calculateActivation(s, predictionTime), s) for s in presentedItems], key=lambda x: x[0])
        if minActivation <= ACTIVATION_THRESHOLD_RETEST:
          stimulus = minActivationStimulus
      if not stimulus:
        # None under that threshold? Add a new item if possible
        if len(presentedItems) < len(self.__stimuli):
          stimulus = self.__stimuli[len(presentedItems)]
      if not stimulus:
        stimulus = minActivationStimulus
      if not stimulus:
        raise ValueError("Could not select any stimulus for presentation")

      #print "Presented items:\n  ", "\n  ".join([str((calculateActivation(s, predictionTime), s.name, s.alpha, map(str, s.presentations))) for s in presentedItems])

      newPresentation = WordItemPresentation()
      presentationStartTime = mainTimer()
      newPresentation.decay = calculateNewDecay(stimulus, presentationStartTime)

      if len(stimulus.presentations) == 0:
        # First presentation of stimulus
        self.__appInterface.learn(stimulus.image, stimulus.name, stimulus.translation)
      else:
        # Second presentations of stimulus
        response = self.__appInterface.test(stimulus.name)
        
        if response.lower() == stimulus.translation.lower():
          self.currentScore += CORRECT_ANSWER_SCORE
          self.__appInterface.updateHighscore(self.currentScore)
          self.__appInterface.displayCorrect(response, stimulus.translation)
          repeat = False
        else:
          stimulus.alpha += ALPHA_ERROR_ADJUSTMENT_SUMMAND
          newPresentation.decay = calculateNewDecay(stimulus, presentationStartTime)
          
          mixedUpWord = self.findMixedUpWord(response)
          if mixedUpWord:
            self.__appInterface.mixedup(stimulus.name, stimulus.translation, mixedUpWord.name, mixedUpWord.translation)
          else:
            self.__appInterface.displayWrong(response, stimulus.translation, stimulus.image)

      newPresentation.time = presentationStartTime
      stimulus.presentations.append(newPresentation)
      
      if inbetweenSessionCountdown.getTime() <= 0:
        imageWordPairs = {}
        imageSequence = []
        for stimulus in self.__stimuli:
          if stimulus.presentations:
            translationData = (stimulus.name, stimulus.translation)
            if stimulus.image in imageWordPairs:
              imageWordPairs[stimulus.image].append(translationData)
            else:
              imageWordPairs[stimulus.image] = [translationData]
              imageSequence.append(stimulus.image)
        
        self.__appInterface.startInbetweenSession([(image, imageWordPairs[image]) for image in imageSequence])
        inbetweenSessionCountdown = CountdownTimer(TEST_BLOCK_DURATION)
