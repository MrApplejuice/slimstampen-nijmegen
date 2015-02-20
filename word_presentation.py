import random

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
    self.__stimuli = stimuli
    
    self.currentScore = 0
    
  def run(self):
    learnSequence = list(self.__stimuli)
    random.shuffle(learnSequence)
    #for stimulus in learnSequence:
    #  self.__appInterface.learn(stimulus["image"], stimulus["word"], stimulus["translation"])
      
    for stimulus in learnSequence:
      repeat = True
      while repeat:
        response = self.__appInterface.test(stimulus["word"])
        
        if response.lower() == stimulus["translation"].lower():
          self.currentScore += 10
          self.__appInterface.updateHighscore(self.currentScore)
          self.__appInterface.displayCorrect(response, stimulus["translation"])
          repeat = False
        else:
          self.__appInterface.displayWrong(response, stimulus["translation"], stimulus["image"])
          self.__appInterface.mixedup("Station", "Bahnhof", "Stadium", "Stadion")
