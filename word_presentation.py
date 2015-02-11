import random

class ApplicationInterface(object):
  class Response:
    NONE = None
    CORRECT = 1
    WRONG = 2
  
  def learn(self, image, word, translation):
    raise NotImplementedError()
  def test(self, word, checkResponseFunction):
    raise NotImplementedError()
  def updateHighscore(self, score):
    raise NotImplementedError()

class AssignmentModel(object):
  def __init__(self, appInterface, stimuli):
    self.__appInterface = appInterface
    self.__stimuli = stimuli
    
    self.currentScore = 0
    
  def run(self):
    learnSequence = list(self.__stimuli)
    random.shuffle(learnSequence)
    for stimulus in learnSequence:
      self.__appInterface.learn(stimulus["image"], stimulus["word"], stimulus["translation"])
      
    for stimulus in learnSequence:
      repeat = True
      while repeat:
        def compare(w1, w2):
          return w1.lower() == w2.lower()
        
        def checkResponse(typedWord):
          if compare(typedWord, stimulus["translation"]):
            self.currentScore += 10
            self.__appInterface.updateHighscore(self.currentScore)
            return ApplicationInterface.Response.CORRECT
          else:
            return ApplicationInterface.Response.WRONG
        
        response = self.__appInterface.test(stimulus["word"], checkResponse)
        if compare(response, stimulus["translation"]):
          repeat = False
