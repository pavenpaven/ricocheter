import pygame

KEY_DICT = dict() # this stores the last frame something was pressed and add it if its not there

def is_keydown(eventlist: [pygame.event], key: str, framecount):
  for i in eventlist:
    if i.type == pygame.KEYDOWN:
      x = i.unicode
      if x==key:
        if not x in KEY_DICT:
          KEY_DICT[x] = framecount
          return True

        if KEY_DICT[x]+2 < framecount:
          KEY_DICT[x] = framecount
          return True
  return False