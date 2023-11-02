import pygame
import src.state as state
import src.animation as animation
from typing import Callable

tile=38
c = lambda f,*x:lambda *y:f(*x, *y)

def load_sprites(segname, filename, change_state, kill: Callable[[int], None]): #um for refrence change_state changes the current global state this was first used to change to a texbox state, kill is just popping the actor element and theirby the actors have a way of dieing 
  with open(filename, "r") as fil:
    txt=fil.read()
  
  txt = txt.split(";\n")
  txt = list(map(lambda x:x.split(":"), txt))

  #for i in txt:
    #print(segname, i[0])
    
  seg = list(filter(lambda x:segname==x[0], txt))
  if not seg==[]:
    seg = seg[0][1].split("\n")
    seg = list(map(lambda x:x.split("-"), seg))
    seg.pop(0)
    for n,i in enumerate(seg[0:len(seg)-1]):
      x = i[1].split(",")
      seg[n][1] =  (float(x[0])*tile, float(x[1])*tile)

  
    out=[]
    for i in seg:
      for f in SPRITE_CLASSES:
        #print(i, f.name)
        if i[0]==f.name:
          if len(i)>2:
            out.append(f(i[1],change_state, kill,extra=i[2]))
          else:
            #print(f,i[1])
            out.append(f(i[1], change_state, kill))
  else:
    out = []

  return out

def give_actors(segname):
  pass
  
def actor_iter(filename: str) -> str:
    with open(filenamem, "r") as fil:
        txt = fil.read()
    txt = txt.split("\n")
    txt = list(filter(lambda x: not ":" in x, txt))
    return txt

def get_actor_save_by_id(identifier: int) -> dict:
    return ACTOR_SAVE_DATA[identifier]

def write_actor_save_by_id(identifier: int, save: dict) -> None:
    ACTOR_SAVE_DATA[identifier] = save


def re(filename, size):
  x=pygame.image.load(filename)
  return pygame.transform.scale(x, size)

class Sprite:
  texture=re("Art/unknown.png", (1,1))
  size=(1,1)
  collision=False
  interactable = False
  INDEX = 0
  IS_ENEMY = False
  IS_BULLET = False
  IS_GLOBALLY_LOADED = False
  IS_GHOST = False
  
  def __init__(self, pos, change_state, kill, extra=""):
    #print(pos)
    #pos = pos.split(",") #stupid string
    #self.pos = (tile*int(pos[0]), tile*int(pos[1]))
    self.pos =pos
    self.change_state = change_state
    self.startup_process(extra)
    self.kill = kill
    self.index = Sprite.INDEX
    Sprite.INDEX += 1

  @property
  def rect(self):
      return pygame.Rect(self.pos, self.size)

  def startup_save(self) -> dict:
      return dict()

  def startup_process(self, extra):
    pass

  def step_on(self, player):
    pass

  def step(self, scene, player): #wtf wtf wtf  wtf wtf wtf wtfd wtf wtf wtfw tfw tfw tfw 
    pass

  def player_action(self):
    pass

  def mouse_over(self):
      pass

  def render(self, scene, framecount):
    scene.blit(self.texture, self.pos)


class Animation_sprite(Sprite):
     anim = ("Art/Cute_earth_with_out_space", (1, 1), 15)
     name = "animation"
    
     def startup_process(self, extra):
         self.ani = animation.Animation.from_dir(*self.anim)

     def render(self, scene, framecount):
         self.ani.update(framecount)
         scene.blit(self.ani.texture, self.pos)

class Earth(Animation_sprite):
    anim = ("Art/Cute_earth_with_out_space", (2.5*tile, 2.5*tile), 15)
    size =(2.5*tile, 2.5*tile)
    name = "earth"

ACTOR_SAVE_DATA = []
SPRITE_CLASSES = [Earth]
