import random
from typing import List, Sequence, NewType, TypeVar, Generic, Callable, Set
from itertools import chain
from src.actor import tile
import src.actor as actor
import src.pickup as pickup
import src.enemy as enemy


NEWLINE = "\n"
Pos = tuple[int, int]
Segname = NewType("Segname", str) # magic
Orientation = NewType("Orientation", int)   
Actor_constructor = tuple[Callable[[None], None], Callable[[None], None]] # change state and kill

T =TypeVar("T")  

class Graph(Generic[T]): # directed
    def __init__(self, nodes: Sequence[T], edges: Sequence[tuple[T, T]]) -> None:
        self.nodes: Sequence[T] = nodes
        self.edges = edges
    
    def __repr__(self) -> str:
        return f"Graph nodes:{NEWLINE.join(list(map(str, self.nodes)))}\n edges:{NEWLINE.join(list(map(str, self.edges)))}"

    def neighbours(self, node: T) -> List[T]:
        return list(map(lambda x: x[1], list(filter(lambda x:x[0]==node, self.edges))))

    def is_neighbours(self, node1: T, node2: T) -> bool:
        return node1 in self.neighbours(node2)
    
    @classmethod
    def without(cls, graph, skarbrada: Set[T]):
        return cls([i for i in graph.nodes if not i in skarbrada], [(i,j) for i,j in graph.edges if (not i in skarbrada) and (not j in skarbrada)])


class Room_prototype:
  NAME = "room prototype"
  INTERVAL = (0, 0)
  TILE_SEGNAME = Segname("")
  def __init__(self) -> None:
      self.NAME =   self.NAME
#  def __eq__(self, other):
 #     if isinstance(other, Room_prototype):
  #        return other.Index==self.Index
   #   return False
  def __repr__(self) -> str:
      return self.NAME
    
  def orientation(self, orientations: list[Orientation]) -> tuple[Segname, Orientation]:
      if len(orientations)>1:
          raise Exception(f"room prototype {Room_prototype} connected to too many rooms")
      return (self.TILE_SEGNAME, orientations[0])

  def populate(self, create_actor: Actor_constructor, room) -> list[actor.Sprite]:
      return [] 
  
Con = int | None

class Room:
    ID = 0
    def __init__(self, prototype: Room_prototype, neighbouring_orientations: list[Orientation]) -> None:
        self.prototype = prototype
        self.connections: list[Con] = [None, None, None, None] #why not tuple ask type thing
        self.segname, self.orientation = prototype.orientation(neighbouring_orientations)
        self.id = self.__class__.ID
        self.__class__.ID += 1

    def __repr__(self) -> str:
        return f"Room: {self.segname}, connected with: {self.connections}, oriented: {('North', 'West', 'South', 'East')[self.orientation % 4]}"
    
    def to_tiles(self) -> str:
        return "" #FIXME
    
    def populate(self, constructor: Actor_constructor) -> list[actor.Sprite]:
        return self.prototype.populate(constructor, self)
    
def link(a:Room, b:Room, orientation: Orientation) -> None: # places 
    a.connections[orientation] = b.id
    b.connections[(orientation+2)%4] = a.id


vec2_add: Callable[[Pos, Pos], Pos] = lambda x,y: (x[0]+y[0], x[1]+y[1]) 

rotate90: Callable[[Pos], Pos] = lambda x: (-x[1], x[0])
def rotate(n:int, x:Pos) -> Pos:
    if n:
        return rotate(n-1, rotate90(x))
    else:
        return x

get_orientations: Callable[[Pos, list[Pos]], list[Orientation]] = lambda x,s: [Orientation(i) for i in range(4) if vec2_add(x, rotate(i, (0, 1))) in s]

def get_rooms(g: Graph[tuple[Room_prototype, Pos]]) -> list[Room]:
    neighbours_pos = [[j[1] for j in g.neighbours(i)] for i in g.nodes]
    rooms = [Room(i[0], get_orientations(i[1], j)) for i,j in zip(g.nodes, neighbours_pos)]
    room_map = dict(zip(g.nodes, rooms))
    for i,j in g.edges:
        link(room_map[i], room_map[j], get_orientations(i[1], [j[1]])[0])
    return rooms
  
class Shop(Room_prototype):
  NAME = "shop room"
  INTERVAL = (1, 1)
  TILE_SEGNAME = Segname("Shop")
  def populate(self, constructor: Actor_constructor, room) -> list[actor.Sprite]:
      return [pickup.Item_sprite((12.5*tile, 2.5*tile), *constructor, "shopkeeper"),
              pickup.Item_sprite((4.5*tile, 2.5*tile), *constructor, "pancake")]
  
  
class Reward(Room_prototype):
  NAME = "reward room"
  INTERVAL = (1, 2)
  TILE_SEGNAME = Segname("Reward_2") # maybe have "Reward" too

  def populate(self, constructor: Actor_constructor, room) -> list[actor.Sprite]:
      return [pickup.Item_sprite((5*tile, 5*tile), *constructor, "pancake"),
              enemy.Rammer((2*tile, 8*tile), *constructor),
              enemy.Rammer((12*tile, 12*tile), *constructor),
              enemy.Ghost((12*tile, 12*tile), *constructor)]

  
class Spawn(Room_prototype):
  NAME = "spawn room"
  INTERVAL = (1, 1)
  TILE_SEGNAME = Segname("Spawn")
  
class Boss(Room_prototype):
  NAME = "boss room"
  INTERVAL = (1, 1)
  TILE_SEGNAME = Segname("Boss_hallway")
  
class Key(Room_prototype):
  NAME = "key room"
  INTERVAL = (1, 1)
  TILE_SEGNAME = Segname("Key")
  def populate(self, constructor: Actor_constructor, room) -> list[actor.Sprite]:
      return [pickup.Item_sprite((7*tile,7*tile), *constructor, "key")]

  
class Branch(Room_prototype):
    NAME = "branch room"
    INTEVAL = None
    TIlE_SEGNAME = Segname("Branch")

    def orientation(self, orientations: list[Orientation]) -> tuple[Segname, Orientation]:
        if len(orientations)==4:
            return (Segname(random.choice(["Branch", "test1"])), Orientation(0))
        elif len(orientations) ==3:
            return (Segname(random.choice(["Hallway_3", "Hallway_4"])), Orientation(([i for i in range(4) if not i in orientations][0]-1) % 4))
        elif len(orientations) ==2:
            return Path.orientation(Path(), orientations) #what the 
        elif len(orientations) == 1:
            return (Segname("Spawn"), orientations[0])


        raise Exception(f"room prototype {Room_prototype} connected to too many rooms or none")

    def populate(self, constructor: Actor_constructor, room) -> list[actor.Sprite]:
        return [enemy.Rammer((7*tile,7*tile), *constructor), enemy.Ghost((0,0), *constructor)]

class Path(Room_prototype):
    NAME = "Path"
    TILE_SEGNAME = Segname("None") # can be multiple diffrent varients and dependent on connections lol 
    
    def orientation(self, orientations: list[Orientation]) -> tuple[Segname, Orientation]:
        if len(orientations) !=2:
            raise Exception(f"room prototype {Room_prototype} connected to too many rooms or few")
        if orientations[0]%2 == orientations[1]%2:
            return (Segname(random.choice(["Hallway", "Hallway_thicc", "Hallway_5", "Battle_room"])), Orientation(orientations[0] % 2))
        if (orientations[0]+1) == orientations[1]:
            x = orientations[0]
        else:
            x = orientations[1]
        return  (Segname(random.choice(["Hallway_turn", "weirdTurn", "Battle_turn", "Battle_turn2"])), Orientation(x))

    def populate(self, constructor: Actor_constructor, room):
        if room.segname == Segname("Battle_room"):
            return [enemy.Rammer((7.5*tile, 7.5*tile), *constructor),
                    enemy.Rammer((1.5*tile, 7.5*tile), *constructor),
                    enemy.Rammer((13.5*tile, 7.5*tile), *constructor),
                    enemy.Turret((13.5*tile, 7.5*tile), *constructor)]
        if room.segname == Segname("Battle_turn") or room.segname == Segname("Battle_turn2"):
            return [enemy.Rammer((6*tile, 12*tile), *constructor),
                    enemy.Rammer((3*tile, 9*tile), *constructor),
                    enemy.Ghost((7.5*tile,7.5*tile), *constructor)]
        return []


NECESSARY_ROOMS = [Shop, Reward, Spawn, Boss, Key] #branch not in NECESSARY_ROOMS



def random_amount_rooms() -> List[tuple[type[Room_prototype], int]]:
    return list(map(lambda x:(x, random.randint(*x.INTERVAL)), NECESSARY_ROOMS))

#def random_amount_
