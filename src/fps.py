import pygame

pygame.font.init()
FPS_FONT = pygame.font.SysFont("roboto", 50)

def render_fps(fps):
  fps = round(fps, 1) # rounds fps to 1 decimal
  return FPS_FONT.render(str(fps), True, (255,255,255))
  