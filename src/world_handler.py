import pygame
import math
import src.player as player
import src.world as world
import src.actor as actor
import src.conf as conf
import src.state as state
import src.pickup as pickup
import key

tile = world.tile

CONTROLLER_SLOTS = [int(conf.conf_search(f"controller_slot{n+1}")) for n in range(5)]

CONTROLLER = conf.conf_search("controller") == "true"
if CONTROLLER:
  pygame.joystick.init()
  if not pygame.joystick.get_count():
    raise Exception("Couldn't find controller, if you dont want to use controller change 'controller' attribute in conf.txt file")
  controller = pygame.joystick.Joystick(0)

def overworld_handler(window, framecount, event_list, music) -> state.State:
  scene.state = state.State.OVERWORLD
  if not scene.tiles:
    scene.load_room("Level/gamefile", None, music)
    print(scene.segname)
  if "lives" in jack.__dict__.keys():
    if jack.lives <= 0:
      globals()["jack"] = player.Player((6.5*tile ,6.5*tile), "Art/Cute_ship_ani_2",(38,38), float(conf.conf_search("speed")))      
      scene.actors = {"Title": [actor.Earth((10*tile,4*tile), scene.change_state ,scene.kill_actor)]}
      scene.load_room("Level/tile_map", "Title", music)
      return state.State.TITLE
   
  graphics(window, music, framecount)
  check_key(event_list, framecount, music)
  return scene.state
  

def graphics(window, music, framecount):
  scene.render(window, jack, music, framecount)

def dot(v, w):
  return v[0]*w[0] + v[1]*w[1]
  
def check_key(event_list, framecount, music):
  keys = pygame.key.get_pressed()
  pygame.key.set_repeat(1, 100000000)
  if not CONTROLLER: #wtf
    vec = [0,0,0,0,0,0]
    for i in event_list:
        if i.type == pygame.KEYDOWN:
            if i.key == pygame.K_a:
                vec[3]=1
    if keys[pygame.K_LEFT] or keys[pygame.K_l] :
      vec[1]+=1
    if keys[pygame.K_RIGHT] or keys[pygame.K_j]:
      vec[1]+=-1
    if keys[pygame.K_UP] or keys[pygame.K_i]:
      vec[0] +=1
    if keys[pygame.K_DOWN] or keys[pygame.K_k]:
      vec[0] +=-1
    if keys[pygame.K_d]:
      vec[4] = 1
    if keys[pygame.K_s] or keys[pygame.K_z]:
      vec[2] =1
    vec[5:] = [keys[pygame.K_q], keys[pygame.K_w], keys[pygame.K_e], keys[pygame.K_r], keys[pygame.K_f]]
    
 # if key.is_keydown(event_list, "x", framecount):
  #  jack.use_button(scene.actors)
  else:
    vec = [0,0,0,0,0,0,0,0,0,0,0]
    vec[1] = -controller.get_axis(0)
    vec[0] = -controller.get_axis(1)
    if abs(vec[1]) < 0.2:
      vec[1] = 0
    if abs(vec[0]) < 0.2:
      vec[0] = 0

    if vec[0] or vec[1]:
      sq = 1/math.sqrt(2)
      (vec[0], vec[1]) = max((1,0), (0,1), (-1,0), (0,-1),
                              (sq, sq), (sq, -sq), (-sq, sq), (-sq, -sq), key = lambda x: dot(x, (vec[0], vec[1])))
      if vec[0]:
        vec[0] /= abs(vec[0])
      if vec[1]:
        vec[1] /= abs(vec[1])

    
    
    if controller.get_button(int(conf.conf_search("controller_reload"))):
      vec[4] = 1
    if controller.get_button(int(conf.conf_search("controller_break"))):
      vec[2] =1

    vec[5:] = list(map(controller.get_button, CONTROLLER_SLOTS))
      
    for i in event_list:
      if i.type == pygame.JOYBUTTONDOWN:
        if i.button == int(conf.conf_search("controller_shoot")):
          vec[3] = 1
  jack.walk(vec, scene, (-vec[1], -vec[0]), music)

  
  if key.is_keydown(event_list, "o", framecount) and is_cheats_on:
      world_commands(music)
  

is_cheats_on = conf.conf_search("cheats")=="True"

def world_commands(music):
    command = input("Enter a command: ")
    if command.startswith("load "):
        scene.load_room("Level/tile_map", command.split(" ")[1], music)
    if command.startswith("noclip "):
        player.NOCLIP[0] = int(command.split(" ")[1])
    if command.startswith("give "):
      jack.get(pickup.ITEM_DICT[command.split(" ")[1]]())
        

scene = world.Map((16,16), (0, tile*2), state.State.OVERWORLD)
#print(scene.tiles)

imag2 = pygame.image.load("Art/jack.png")
imag2 = pygame.transform.scale(imag2, (20,18))  # lots of globals its essentialy a object or singleton because of the name space idk maybe i should make a class


jack = player.Player((6.5*tile ,6.5*tile), "Art/Cute_ship_ani_2",(38,38), float(conf.conf_search("speed")))
