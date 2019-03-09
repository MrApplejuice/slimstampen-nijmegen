
def make_adhoc_object(**kwargs):
    class KWARGS:
        pass
    
    for k, v in kwargs.items():
        setattr(KWARGS, k ,v)
        
    return KWARGS()


class PIXIInterface:
    def __init__(self, dom_element):
        print(make_adhoc_object(backgroundColor = 0xFF0000)) 
        print(make_adhoc_object(backgroundColor = 0xFF0000).backgroundColor)
        
        self.__pixi = do_new(PIXI.Application,
            800, 600, 
            {
                "backgroundColor": 0xFF0000
            })
        dom_element.appendChild(self.__pixi.view)
    
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
