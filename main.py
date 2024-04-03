import pygame
pygame.init()
pygame.display.init()
window = pygame.display.set_mode((608,700), pygame.DOUBLEBUF, 32)
pygame.mixer.init()

import math
import sys
import src.conf as conf
import src.fps as fps
import src.world as world
import src.state as state
import state_handler
import src.music


tile = world.tile

def post_graphics(fps_surface):
  window.blit(fps_surface, (10,10))
  pygame.display.update()
  window.fill((0,0,0))

def main():
  running = True
  clock = pygame.time.Clock()
  framecount = 0
  last_pressed = 0 
  fps_surface = fps.render_fps(0)
  current_state = state.State.TITLE
  music = src.music.Music("Level/theme_info")
  while running:
    clock.tick(30)
    framecount+=1
    event_list = pygame.event.get() 
    if framecount % 10 == 0:
        fps_surface=fps.render_fps(clock.get_fps())

    x = state_handler.state_handling(current_state, window, framecount, event_list, music)
    state_handler.previous.state = current_state
    current_state = x
    
    post_graphics(fps_surface)

    if current_state == None:
      print("exits through state being None")
      pygame.quit()
      running = False
    
    for event in event_list:
      if event.type == pygame.QUIT:
        pygame.quit()
        running = False

main()
