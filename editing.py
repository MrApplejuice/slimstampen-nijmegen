# -*- coding: utf-8 -*-

from psychopy import core, event

def recordKeyboardInputs(win, textField, finish_key='return', clock=None, give_sentence_onset=False, countdown=None, shadowText=None, shadowTextColor=(0.5, 0.5, 0.5), idleFunction=None):
  if clock is None:
    clock = core.Clock()    
    
  KEY_TRANSLATION_TABLE = {'pound': '#', 'comma': ',', 'period': '.', 'plus': '+', 'minus': '-', 'space': ' '}
  
  event.clearEvents()
  
  doRecord = True
  text = ""
  history = []
  sentenceOnset = None
  
  if textField is not None:
    normalTextColor = textField.color
  
  while doRecord and ((countdown is None) or (countdown.getTime() > 0)):
    if idleFunction:
      idleFunction()
    if textField is not None:
      if text or not shadowText:
        textField.color = normalTextColor
        textField.text = text
      elif shadowText:
        textField.color = shadowTextColor
        textField.text = shadowText
    win.flip()

    keys = event.getKeys(timeStamped=clock)
    if sentenceOnset is None:
      sentenceOnset = clock.getTime()
    
    for key in keys:
      rawkey = key[0]
      
      # Translate keys that should be written out
      if key[0] in KEY_TRANSLATION_TABLE:
        key = (KEY_TRANSLATION_TABLE[key[0]], key[1])
        
      if key[0] in u'abcdefghijklmnopqrstuvwxyz0123456789 .,!?-;:äüöß':
        text += key[0]
      elif key[0] == finish_key:
        doRecord = False
      elif key[0] == "backspace":
        text = text[:-1]
        
      history.append({'key': rawkey, 'time': key[1], 'current_text': text})
      if not doRecord:
        break

  if textField is not None:
    textField.color = normalTextColor
    if (not text) and shadowText:
      textField.text = ""
  
  if give_sentence_onset:
    return history, sentenceOnset
  return history
