from psychopy import core, event

def recordKeyboardInputs(win, textField, finish_key='return', clock=None, give_sentence_onset = False, countdown=None):
  if clock is None:
    clock = core.Clock()    
    
  KEY_TRANSLATION_TABLE = {'pound': '#', 'comma': ',', 'period': '.', 'plus': '+', 'minus': '-', 'space': ' '}
    
  event.clearEvents()
  
  doRecord = True
  text = ""
  history = []
  sentenceOnset = None
    
  while doRecord and ((countdown is None) or (countdown.getTime() > 0)):
    textField.setText(text)
    win.flip()
    keys = event.getKeys(timeStamped=clock)
    if sentenceOnset is None:
      sentenceOnset = clock.getTime()
    
    for key in keys:
      rawkey = key[0]
      
      # Translate keys that should be written out
      if key[0] in KEY_TRANSLATION_TABLE:
        key = (KEY_TRANSLATION_TABLE[key[0]], key[1])
        
      if key[0] in 'abcdefghijklmnopqrstuvwxyz0123456789 .,!?-;:':
        text += key[0]
      elif key[0] == finish_key:
        doRecord = False
      elif key[0] == "backspace":
        text = text[:-1]
        
      history.append({'key': rawkey, 'time': key[1], 'current_text': text})
      if not doRecord:
        break
  
  if give_sentence_onset:
    return history, sentenceOnset
  return history