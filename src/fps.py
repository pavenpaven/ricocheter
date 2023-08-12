import pygame

pygame.font.init()
FONT = pygame.font.Font("Art/m3x6.ttf", 50)

def render_fps(fps):
  fps = round(fps, 1) # rounds fps to 1 decimal
  return FONT.render(str(fps), True, (255,255,255))
  
