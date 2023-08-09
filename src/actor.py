import pygame
import src.state as state

tile=30

def load_sprites(segname, filename, change_state):
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
            out.append(f(i[1],change_state,extra=i[2]))
          else:
            #print(f,i[1])
            out.append(f(i[1], change_state))
  else:
    out = []

  return out

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
  def __init__(self, pos, change_state, extra=""):
    #print(pos)
    #pos = pos.split(",") #stupid string
    #self.pos = (tile*int(pos[0]), tile*int(pos[1]))
    self.pos =pos
    self.change_state = change_state
    self.startup_process(extra)

  def startup_save(self) -> dict:
      return dict()

  def startup_process(self, extra):
    pass

  def step_on(self):
    pass

  def step(self):
    pass

  def player_action(self):
    pass
    
  def render(self, scene):
    scene.blit(self.texture, self.pos)

ACTOR_SAVE_DATA = []
SPRITE_CLASSES = []
