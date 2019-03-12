import random
import math

def enter_leave_print(text):
    def decorate(f):
        def result(*args, **kwargs):
            print("Enter:", text)
            try:
                return f(*args, **kwargs)
            finally:
                print("Leave:", text)
        return result
    return decorate


def py_min(seq, key=None):
    if key is None:
        return min(seq)
    else:
        m = min([key(x) for x in seq])
        for x in seq:
            if key(x) == m:
                return x


class WordItemPresentation:
    def __init__(self, time=0, decay=0):
        self.decay = decay
        self.time = time
    
    def __str__(self):
        return "(Presentation: decay={d} time={t})".format(d=self.decay, t=self.time)

class WordItem:
    def __init__(self, name):
        self.name = name
        self.alpha = .25
        self.presentations = []

def _calculateDecayFromActivation(x, alpha):
    """
    Referred to as "d" in the equations
    """
    c = 0.2
    return c * math.exp(x) + alpha

def calculateActivation(wordItem, time, leaveout=0):
    if len(wordItem.presentations) - leaveout <= 0:
        raise ValueError("activaton undefined for item that was not presented yet")
    else:
        #print "Using ", [(time - presentation.time, presentation.decay) for presentation in wordItem.presentations[:len(wordItem.presentations) - leaveout]]
        return math.log(sum([(time - presentation.time)**(-presentation.decay) for presentation in wordItem.presentations[:len(wordItem.presentations) - leaveout]])) #calculate activation of second to last

def calculateNewDecay(wordItem, time, leaveout=0):
    if len(wordItem.presentations) - leaveout <= 0:
        return _calculateDecayFromActivation(0, wordItem.alpha)
    else:
        m = calculateActivation(wordItem, time, leaveout=leaveout)
        return _calculateDecayFromActivation(m, wordItem.alpha)


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
    
    @property
    def done(self):
        return True


class AssignmentModel(object):
    __app_interface = None #: :type app_interface: ApplicationInterface
    
    def __init__(self, appInterface, stimuli):
        self.__app_interface = appInterface 

        def makeWordItem(s):
            wi = WordItem(s["word"].strip().lower())
            wi.translation = s["translation"].strip().lower()
            wi.image = s["image"].strip()
            return wi

        self.__stimuli = [makeWordItem(s) for s in stimuli]

        self.currentScore = 0

        self.__main_time = js_time()
        self.__total_test_time = js_time()
        self.__inbetween_session_time = js_time()

        self.__state = None

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

    @property
    def main_timer(self):
        return (js_time() - self.__main_time) / 1000

    def __new_presentation(self):
        presented_items = [
            x for x in self.__stimuli if len(x.presentations) > 0
        ]
        stimulus = None
        min_activation_stimulus = None
        
        if len(presented_items) > 0:
            # Select item from presented items with activation <=
            # ACTIVATION_THRESHOLD_RETEST
            predictionTime = self.main_timer + ACTIVATION_PREDICTION_TIME_OFFSET
            activation_pairs = [
                (calculateActivation(s, predictionTime), s) 
                for s in presented_items
            ]
            minActivation, min_activation_stimulus = \
                py_min(activation_pairs, key=lambda x: x[0])
            if minActivation <= ACTIVATION_THRESHOLD_RETEST:
                stimulus = min_activation_stimulus
        if not stimulus:
            # None under that threshold? Add a new item if possible
            if len(presented_items) < len(self.__stimuli):
                stimulus = self.__stimuli[len(presented_items)]
        if not stimulus:
            stimulus = min_activation_stimulus
        if not stimulus:
            raise ValueError("Could not select any stimulus for presentation")

        new_presentation = WordItemPresentation()
        presentation_start_time = self.main_timer
        new_presentation.decay = \
            calculateNewDecay(stimulus, presentation_start_time)
            
        self.__state = {
            "type": None,
            "answer": None,
            "item": stimulus,
            "start_time": presentation_start_time,
            "new_presentation": new_presentation,
        }
        
        if len(stimulus.presentations) == 0:
            self.__state["type"] = "learn"
            self.__app_interface.learn(
                stimulus.image, stimulus.name, stimulus.translation)
        else:
            print("MUST TEST NOW")

    @enter_leave_print("__add_presentation")
    def __add_presentation(self, stimulus, presentation, start_time):
        presentation.time = start_time
        stimulus.presentations.append(presentation)

    @enter_leave_print("iter_run")
    def iter_run(self):
        if not self.__app_interface.done:
            return
        
        if self.__state is None:
            self.__state = "instructions"
            self.__app_interface.displayInstructions()
        elif self.__state == "instructions":
            self.__new_presentation()
        elif not isinstance(self.__state, dict):
            print(f"ERROR: Invalid state: {self.__state}")
        elif self.__state.get("type") == "learn":
            self.__add_presentation(
                self.__state["item"],
                self.__state["new_presentation"],
                self.__state["start_time"])
            self.__new_presentation()
        else:
            print("ERROR: ULTIMATE ELSE")
        
        


    def __run(self):
        while totalTestTimer.getTime() > 0:


            # print "Presented items:\n    ", "\n
            # ".join([str((calculateActivation(s, predictionTime), s.name, s.alpha,
            # map(str, s.presentations))) for s in presentedItems])


            if len(stimulus.presentations) == 0:
                # First presentation of stimulus
                #self.__app_interface.learn(
                #        stimulus.image, stimulus.name, stimulus.translation)
                pass
            else:
                # Second presentations of stimulus
                response = self.__app_interface.test(stimulus.name)

                if response.lower() == stimulus.translation.lower():
                    self.currentScore += CORRECT_ANSWER_SCORE
                    self.__app_interface.updateHighscore(self.currentScore)
                    self.__app_interface.displayCorrect(response, stimulus.translation)
                    repeat = False
                else:
                    stimulus.alpha += ALPHA_ERROR_ADJUSTMENT_SUMMAND
                    newPresentation.decay = calculateNewDecay(
                            stimulus, presentationStartTime)

                    mixedUpWord = self.findMixedUpWord(response)
                    if mixedUpWord:
                        self.__app_interface.mixedup(
                                stimulus.name, stimulus.translation, mixedUpWord.name, mixedUpWord.translation)
                    else:
                        self.__app_interface.displayWrong(
                                response, stimulus.translation, stimulus.image)

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

                self.__app_interface.startInbetweenSession(
                        [(image, imageWordPairs[image]) for image in imageSequence])
                inbetweenSessionCountdown = CountdownTimer(TEST_BLOCK_DURATION)
