import random

class ApplicationInterface(object):
  def learn(self, image, word, translation):
    raise NotImplementedError()
  def test(self, word):
    raise NotImplementedError()

class AssignmentModel(object):
  def __init__(self, appInterface, stimuli):
    self.__appInterface = appInterface
    self.__stimuli = stimuli
    
  def run(self):
    learnSequence = list(self.__stimuli)
    random.shuffle(learnSequence)
    for stimulus in learnSequence:
      self.__appInterface.learn(stimulus["image"], stimulus["word"], stimulus["translation"])
      
    for stimulus in learnSequence:
      repeat = True
      while repeat:
        response = self.__appInterface.test(stimulus["word"])
        if response.lower() == stimulus["translation"].lower():
          repeat = False
