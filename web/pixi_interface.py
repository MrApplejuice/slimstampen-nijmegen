import re

class Confirmable:
    _confirmable_initialized = False
    
    def __init__(self):
        if self._confirmable_initialized:
            return
        self._confirmable_initialized = True
        print("INIT CONFIRMABLE")
        
        self._Confirmable__call = None
        window.addEventListener("keydown", self._confirmable__button_pressed)
        
        jQuery(self.pixi.view).on("click", self._confirmable__clicked)
        
        self._confirm__timeout = None
    
    def _confirmable_confim(self):
        if self._confirm__timeout is not None:
            window.clearTimeout(self._confirm__timeout)
            self._confirm__timeout = None
        if self._Confirmable__call is not None:
            call = self._Confirmable__call
            self._Confirmable__call = None
            call()
        
    def _confirmable__clicked(self, event):
        self._confirmable_confim()
    
    def _confirmable__button_pressed(self, event):
        if event.key == "Enter":
            self._confirmable_confim()

    def confirm(self, call):
        self._Confirmable__call = call
        
    def timed_confirm(self, call, timeout=None):
        self.confirm(call)
        if timeout is not None:
            self._confirm__timeout = window.setTimeout(
                lambda *_: self._confirmable_confim(),
                1000 * timeout)
    

class InstructionsMixin(Confirmable):
    pixi = None
    
    def __init__(self):
        super().__init__()
        
        self._inst__active = False
        self._inst__current_index = None
        
        self._inst__instructions = None
        jQuery.ajax({
            "url": "resources/instructions.txt",
        }).done(self.__assign_instructions)
        
        self._inst__text_field = do_new(
            PIXI.Text,
            "",
            {
                "fontFamily": "Arial",
                "fontSize": 24,
                "fill": 0x000000,
            })
        
    def __assign_instructions(self, text):
        self._inst__instructions = [
            t.strip() for t in 
            re.split("-{5,}", text)
        ]
        if self._inst__active:
            self.displayInstructions()

    def displayInstructions(self):
        self._done = False
        
        if not self._inst__active:
            self.pixi.stage.addChild(self._inst__text_field)
        self._inst__active = True
        
        self.pixi.ticker.stop()
        
        if self._inst__instructions:
            if self._inst__current_index is None:
                self._inst__current_index = 0;
            else:
                self._inst__current_index += 1
            if self._inst__current_index >= len(self._inst__instructions):
                self._inst__current_index = None
                self._inst__active = False
                self._done = True
                self.pixi.stage.removeChild(self._inst__text_field)
                self.pixi.ticker.start()
            else:
                text = self._inst__instructions[self._inst__current_index]
                self._inst__text_field.text = text
                self.pixi.render()
                self.confirm(self.displayInstructions)
                
class LearnMixin(Confirmable):
    pixi = None
    
    LEARN_WAIT_TIMES = [15.0, 15.0] # maximum presentation times before program automatically continues, , PP can move on self-paced earlier
    ANIMATION_TIME = 0.01
    
    TEXT_HEIGHT = 0.1
    
    
    def __init__(self):
        super().__init__()
        
        self._learn__image_sprite = None
        self._learn__loader = do_new(PIXI.Loader)
        
        self._learn__word_sprite = do_new(
            PIXI.Text,
            "",
            {
                "fontFamily": "Arial",
                "fontSize": 24,
                "fill": 0x000000,
            })
        self._learn__word_sprite.position.x = 200
        self._learn__word_sprite.position.y = 500

        self._learn__translation_sprite = do_new(
            PIXI.Text,
            "",
            {
                "fontFamily": "Arial",
                "fontSize": 24,
                "fill": 0x000000,
            })
        self._learn__translation_sprite.position.x = 500
        self._learn__translation_sprite.position.y = 500
        
    def _learn__destroy_image(self):
        if self._learn__image_sprite:
            self.pixi.stage.removeChild(self._learn__image_sprite)
            self._learn__image_sprite.destroy()
            self._learn__image_sprite = None
    
    def _learn__create_image_sprite(self, image_url):
        sprite = do_new(PIXI.Sprite["from"], 
            self._learn__loader.resources[image_url].texture)
        sprite.position.set(100, 50)
        x_scale = 600 / sprite.texture.orig.width
        y_scale = (500 - 2 * sprite.position.y) / sprite.texture.orig.height
        scale = min(x_scale, y_scale)
        sprite.scale = do_new(PIXI.Point, scale, scale)
        print("scale:", scale)
         
        self._learn__image_sprite = sprite
        self.pixi.stage.addChild(self._learn__image_sprite)
        
        self.pixi.render()
    
    def learn(self, image, word, translation):
        self._done = False
        
        self.pixi.ticker.stop()
        
        self._learn__destroy_image()
        
        image_url = "resources/images/" + image
        if self._learn__loader.resources[image_url]:
            self._learn__create_image_sprite(image_url)
        else:
            self._learn__loader.add(image_url)
            self._learn__loader.load(
                lambda *_: self._learn__create_image_sprite(image_url))
        
        self._learn__word_sprite.text = word
        
        self._learn__translation_sprite.text = translation
        self._learn__translation_sprite.visible = False
        
        self.pixi.stage.addChild(self._learn__word_sprite)
        self.pixi.stage.addChild(self._learn__translation_sprite)
        
        self.pixi.render()
        
        self.timed_confirm(self._learn__show_translation, self.LEARN_WAIT_TIMES[0])
        
    def _learn__show_translation(self):
        self._learn__translation_sprite.visible = True
        self.pixi.render()
        self.timed_confirm(self._learn__learn_done, self.LEARN_WAIT_TIMES[1])
    
    def _learn__learn_done(self):
        self.pixi.stage.removeChild(self._learn__image_sprite)
        self.pixi.stage.removeChild(self._learn__word_sprite)
        self.pixi.stage.removeChild(self._learn__translation_sprite)
        self.pixi.ticker.start()
        self._done = True


class TestMixin(Confirmable):
    pixi = None
    
    CORRECT_WORD_WAIT_TIME = 1
    
    def __init__(self, dom_element):
        super().__init__()
        
        self.__test_entered_word_callback = None
        
        self._test__word_sprite = do_new(
            PIXI.Text,
            "",
            {
                "fontFamily": "Arial",
                "fontSize": 24,
                "fill": 0x000000,
            })
        self._test__word_sprite.position.x = 200
        self._test__word_sprite.position.y = 500
        self._test__word_sprite.visible = False
        self.pixi.stage.addChild(self._test__word_sprite)
        
        self._test__text_input = jQuery('<input type="text" value="" />')
        self._test__text_input.css("position", "absolute")
        self._test__text_input.css("left", "500")
        self._test__text_input.css("top", "495")
        self._test__text_input.css("font-size", "24px")
        self._test__text_input.css("color", "black")
        self._test__text_input.css("display", "none")
        jQuery(dom_element).append(self._test__text_input)
    
    def _test__show_words(self, word, translation, real_translation=None):
        self._test__word_sprite.text = word
        
        self._test__translation = translation
        self._test__word_sprite.visible = True
        
        self._test__text_input.val(translation)
        self._test__text_input.css("display", "block")
        self._test__text_input.css("color", "")
        self._test__text_input.focus()
    
    def test(self, word, translation, image, entered_word_callback=None):
        self._done = False
        
        self.__test_entered_word_callback = entered_word_callback
        
        self._test__show_words(word, "")
        
        self.pixi.ticker.stop()
        self.pixi.render()
        
        self.confirm(self._test__confimed)
        
    def displayCorrect(self, word, real_translation):
        self._done = False
        self._test__show_words(word, real_translation)
        self._test__text_input.css("color", "green")
        
        window.setTimeout(
            lambda *_: self._test__confimed(),
            1000 * self.CORRECT_WORD_WAIT_TIME)
        
    def _test__confimed(self):
        self._test__text_input.css("display", "none")
        self._test__word_sprite.visible = False
        
        if self.__test_entered_word_callback is not None:
            self.__test_entered_word_callback(self._test__text_input.val())
        self.__test_entered_word_callback = None
        
        self.pixi.ticker.start()
        self._done = True

class PIXIInterface(InstructionsMixin, LearnMixin, TestMixin):
    def __init__(self, dom_element):
        self.__done = True
        self.done_callback = None
        
        self.pixi = do_new(PIXI.Application,
            800, 600, 
            {
                "backgroundColor": 0xFF0000
            })
        dom_element.appendChild(self.pixi.view)
        window.pixi_app = self.pixi
        
        LearnMixin.__init__(self)
        InstructionsMixin.__init__(self)
        TestMixin.__init__(self, dom_element)

    @property
    def _done(self):
        return self.__done
    
    @_done.setter
    def _done(self, v):
        call = not self.__done and v 
        self.__done = v
        if call and self.done_callback != None:
            self.done_callback()

    @property
    def done(self):
        return self._done
    
    def displayWrong(self, typedWord, correctAnswer, image):
        raise NotImplementedError()

    def mixedup(self, leftUpper, leftLower, rightUpper, rightLower):
        raise NotImplementedError()

    def updateHighscore(self, score):
        print(f"Current score: {score}")

    def startInbetweenSession(self, imageWordPairs):
        raise NotImplementedError()
