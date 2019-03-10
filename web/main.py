from pixi_interface import PIXIInterface
from word_presentation import AssignmentModel

def determineTextWidth(fontStimulus):
    # Determine text width using psychopy's pyglet infrastructure
    glyphList = fontStimulus._font.get_glyphs(fontStimulus.text)
    thisPixWidth = sum([0] + [x.advance for x in glyphList])
    return thisPixWidth * fontStimulus.height / fontStimulus._fontHeightPix / 1.5


def setLineStrikethrough(textStim, lineStim):
    lineStim.start = (textStim.pos[0], textStim.pos[1] - 0.01)
    lineStim.end = (textStim.pos[0] + determineTextWidth(textStim), textStim.pos[1] - 0.01)


IMAGES_SIZE = 1.3
IMAGES_LOCATION = (0, 1 - (IMAGES_SIZE / 2 + 0.05))

def load_all_images(imagePathList):
    result = {}
    for path in imagePathList:
        if path not in result:
            pass
            # # if not os.path.exists(path):
            # #  raise ValueError("Image {} does not exist".format(path))
            #imageStim = visual.ImageStim(win, pos=IMAGES_LOCATION)
            #imageStim.image = path
            #imageStim.size *= IMAGES_SIZE / imageStim.size[1]
        #result[path] = imageStim
    return result


def main():
    stimuli = [
        {
            "word": "test",
            "translation": "ttest",
            "image": "test.png"
        }
    ] * 10
    
    pixi_interface = PIXIInterface(document.body)
    
    model = AssignmentModel(pixi_interface, stimuli)
    model.iter_run()
    #load_all_images(imagePathList)

