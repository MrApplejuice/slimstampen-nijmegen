import random

class ApplicationInterface(object):
  def learn(self, image, word, translation):
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
