import re

class InstructionsMixin:
    pixi = None
    
    def __init__(self):
        self._done = True
        self.__active = False
        self.__current_index = None
        
        self.__instructions = None
        jQuery.ajax({
            "url": "resources/instructions.txt",
        }).done(self.__assign_instructions)
        
        self.__text_field = do_new(
            PIXI.Text,
            "",
            {
                "fontFamily": "Arial",
                "fontSize": 24,
                "fill": 0x000000,
            })
        
        addEventListener("keydown", self.__button_pressed)
        
    def __assign_instructions(self, text):
        self.__instructions = [
            t.strip() for t in 
            re.split("-{5,}", text)
        ]
        if self.__active:
            self.displayInstructions()

    def __button_pressed(self, event):
        if self.__active and self.__instructions:
            if event.key == "Enter":
                self.displayInstructions()

    def displayInstructions(self):
        self._done = False
        
        if not self.__active:
            self.pixi.stage.addChild(self.__text_field)
        self.__active = True
        
        self.pixi.ticker.stop()
        
        if self.__instructions:
            if self.__current_index is None:
                self.__current_index = 0;
            else:
                self.__current_index += 1
            if self.__current_index >= len(self.__instructions):
                self.__current_index = None
                self.__active = False
                self._done = True
                self.pixi.stage.removeChild(self.__text_field)
                self.pixi.ticker.start()
            else:
                text = self.__instructions[self.__current_index]
                self.__text_field.text = text
                self.pixi.render()
                
        


class PIXIInterface(InstructionsMixin):
    def __init__(self, dom_element):
        self.pixi = do_new(PIXI.Application,
            800, 600, 
            {
                "backgroundColor": 0xFF0000
            })
        dom_element.appendChild(self.pixi.view)
        window.pixi_app = self.pixi
        
        InstructionsMixin.__init__(self)
        
        self.__done = True

    @property
    def _done(self):
        return self.__done
    
    @_done.setter
    def _done(self, v):
        self.__done = v

    @property
    def done(self):
        return self._done
    
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

    def startInbetweenSession(self, imageWordPairs):
        raise NotImplementedError()
