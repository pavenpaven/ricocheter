import random
from typing import List, Sequence, NewType, TypeVar, Generic, Callable, Set
from itertools import chain

NEWLINE = "\n"
Pos = tuple[int, int]
Segname = NewType("Segname", str) # magic
Orientation = NewType("Orientation", int)   

T =TypeVar("T")  

class Graph(Generic[T]): # directed
    def __init__(self, nodes: Sequence[T], edges: Sequence[tuple[T, T]]):
        self.nodes: Sequence[T] = nodes
        self.edges = edges
    
    def __repr__(self):
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
  def __init__(self):
      self.NAME =   self.NAME
#  def __eq__(self, other):
 #     if isinstance(other, Room_prototype):
  #        return other.Index==self.Index
   #   return False
  def __repr__(self):
      return self.NAME
    
  def orientation(self, orientations: list[Orientation]) -> tuple[Segname, Orientation]:
      if len(orientations)>1:
          raise Exception(f"room prototype {Room_prototype} connected to too many rooms")
      return (self.TILE_SEGNAME, orientations[0])

Con = int | None

class Room:
    ID = 0
    def __init__(self, prototype: Room_prototype, neighbouring_orientations: list[Orientation]) -> None:
        self.prototype = prototype
        self.connections: list[Con] = [None, None, None, None] #why not tuple ask type thing
        self.segname, self.orientation = prototype.orientation(neighbouring_orientations)
        self.id = self.__class__.ID
        self.__class__.ID += 1

    def __repr__(self):
        return f"Room: {self.segname}, connected with: {self.connections}, oriented: {('North', 'West', 'South', 'East')[self.orientation % 4]}"
    
    def to_tiles(self) -> str:
        return "" #FIXME

def link(a:Room, b:Room, orientation: Orientation) -> None: # places 
    a.connections[orientation] = b.id
    b.connections[(orientation+2)%4] = a.id


vec2_add: Callable[[Pos, Pos], Pos] = lambda x,y: (x[0]+y[0], x[1]+y[1]) 

rotate90 = lambda x: (-x[1], x[0])
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
  
class Reward(Room_prototype):
  NAME = "reward room"
  INTERVAL = (1, 2)
  TILE_SEGNAME = Segname("Reward")
  
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

class Branch(Room_prototype):
    NAME = "branch room"
    INTEVAL = None
    TIlE_SEGNAME = Segname("Branch")

    def orientation(self, orientations: list[Orientation]) -> tuple[Segname, Orientation]:
        if len(orientations)==4:
            return (Segname("Branch"), Orientation(0))
        elif len(orientations) ==3:
            return (Segname("Hallway_3"), Orientation(([i for i in range(4) if not i in orientations][0]-1) % 4))
        elif len(orientations) ==2:
            return Path.orientation(Path(), orientations) #what the 
        elif len(orientations) == 1:
            return (Segname("Spawn"), orientations[0])


        raise Exception(f"room prototype {Room_prototype} connected to too many rooms or none")

class Path(Room_prototype):
    NAME = "Path"
    TILE_SEGNAME = Segname("None") # can be multiple diffrent varients and dependent on connections lol 
    
    def orientation(self, orientations: list[Orientation]) -> tuple[Segname, Orientation]:
        if len(orientations) !=2:
            raise Exception(f"room prototype {Room_prototype} connected to too many rooms or few")
        if orientations[0]%2 == orientations[1]%2:
            return (Segname(random.choice(["Hallway", "Hallway_thicc"])), Orientation(orientations[0] % 2))
        if (orientations[0]+1) == orientations[1]:
            x = orientations[0]
        else:
            x = orientations[1]
        return  (Segname("Hallway_turn"), Orientation(x))

   


NECESSARY_ROOMS = [Shop, Reward, Spawn, Boss, Key] #branch not in NECESSARY_ROOMS



def random_amount_rooms() -> List[tuple[type[Room_prototype], int]]:
    return list(map(lambda x:(x, random.randint(*x.INTERVAL)), NECESSARY_ROOMS))

#def random_amount_
