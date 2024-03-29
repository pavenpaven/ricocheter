import pygame
import src.player as player
import src.world as world
import src.actor as actor
import src.conf as conf
import src.state as state
import key

tile = world.tile

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

def check_key(event_list, framecount, music):
  keys = pygame.key.get_pressed()
  pygame.key.set_repeat(1, 100000000)
  if True: #wtf
    vec = [0,0,0,0,0]
    for i in event_list:
        if i.type == pygame.KEYDOWN:
            if i.key == pygame.K_c:
                vec[3]=1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
      vec[1]+=1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
      vec[1]+=-1
    if keys[pygame.K_w] or keys[pygame.K_UP]:
      vec[0] +=1
    if keys[pygame.K_DOWN]:
      vec[0] +=-1
    if keys[pygame.K_r]:
      vec[4] = 1
    if keys[pygame.K_s] or keys[pygame.K_z]:
      vec[2] =1
    jack.walk(vec, scene, (-vec[1], -vec[0]), music)
  if key.is_keydown(event_list, "x", framecount):
    jack.use_button(scene.actors)

  if key.is_keydown(event_list, "o", framecount) and is_cheats_on:
      world_commands(music)

is_cheats_on = conf.conf_search("cheats")=="True"

def world_commands(music):
    command = input("Enter a command: ")
    if command.startswith("load "):
        scene.load_room(conf.conf_search("starting_filename"), command.split(" ")[1], music)
    if command.startswith("noclip "):
        player.NOCLIP[0] = int(command.split(" ")[1])
        

scene = world.Map((16,16), (0, tile*2), state.State.OVERWORLD)
#print(scene.tiles)

imag2 = pygame.image.load("Art/jack.png")
imag2 = pygame.transform.scale(imag2, (20,18))  # lots of globals its essentialy a object or singleton because of the name space idk maybe i should make a class


jack = player.Player((6.5*tile ,6.5*tile), "Art/Cute_ship_ani_2",(38,38), float(conf.conf_search("speed")))
