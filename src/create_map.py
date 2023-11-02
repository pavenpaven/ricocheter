from itertools import product, combinations, chain, starmap, accumulate, pairwise
from functools import reduce
import math
from typing import TypeVar, List, Sequence, NewType, Union, Callable, Any
from src.random_rooms import Graph, Room_prototype, Branch, T, Path, Pos, Orientation, Segname, Room
import src.random_rooms as random_rooms
from itertools import product
import random
import src.world as world
from src.world import tile 
import src.world_handler as world_handler
import src.music as music
import src.state as state
import time

from src.random_rooms import Spawn,Boss,Reward,Shop,Key #FIXME

tile = world.tile
FILENAME = "Level/gamefile"

def mapgen_handler(music): # wtf
  generate_map(world_handler.scene, music)
  world_handler.scene.tiles = []
  return state.State.OVERWORLD
  
def create_board(n: int) -> Graph[tuple[int, int]]:
  nodes = list(product(range(n), range(n)))
  edges = []
  for x in range(n-1):
    for y in range(n-1):
      edges.append(((x, y), (x+1, y)))
      edges.append(((x+1, y), (x, y)))
      edges.append(((x, y), (x, y+1)))
      edges.append(((x, y+1), (x, y)))
  return Graph(nodes, edges)

def lookup(tab: list[tuple[T, int, T|None]], node: T) -> int: # dont look at this function
  g: Callable[[tuple[T,int, T|None]], Any] = lambda x:x[0]==node
  x = list(filter(g, tab))
  if not x:
    raise Exception(str(node) + " not in table")
  return tab.index(x[0])

def f(table: list[tuple[T, int, T | None]], node: T|None) -> List[T]:
  if node is None:
    return []
  return f(table, table[lookup(table, node)][2])+[node]

def dist(a:Pos ,b:Pos) -> float:
    return math.sqrt(((a[0]-b[0])**2) + ((a[1]-b[1])**2))

def dijkstra(graph: Graph[Pos], start: Pos, dest: Pos) -> List[Pos] | None:
  visited = []
  unvisited = graph.nodes
  table = [(x, 10000, None) for x in filter(lambda x:x!=start, graph.nodes)] + [(start, 0, None)] #10000 == math.inf lol
  while unvisited:
    table.sort(key = lambda x:x[1] + dist(x[0], dest)) # a* i think
    node = list(filter(lambda x:x[0] in unvisited, table))[0]
    for i in graph.neighbours(node[0]):
      ind = lookup(table, i)
      if table[lookup(table, node[0])][1]+1<table[ind][1]:
        table[ind]=(i, table[lookup(table, node[0])][1]+1, node[0])
    
    visited.append(node[0])
    unvisited.remove(node[0])
    if table[lookup(table, dest)][1] < 999:
      break
  if table[lookup(table, dest)][1] < 999:
    return f(table, dest)
  return None # obosolete but i guess more clear


def generate_map(scene: world.Map, music: music.Music) -> Segname: #Note that central branch needs to be edge branch (i.e only connected to one other branch) and g contains no loops and branches are the only nodes with degree higher than 1 and cannot have degree higher than 4
    start = time.perf_counter()
    random_rooms.Room.ID = 0 # yes its that bad
    while True:
        try:
            A = [Branch(),Branch(),Branch(), Branch(), Spawn(), Reward(), Reward(), Shop(), Key(), Boss()]
            g = Graph[Room_prototype](A, [(A[0],A[1]),(A[1],A[0]),(A[1],A[2]),(A[2],A[1]), (A[2], A[3]), (A[3], A[2]),  (A[3],A[4]), (A[4], A[3]), (A[3],A[5]), (A[0], A[6]), (A[2], A[7]), (A[0], A[8]), (A[1], A[9])])

            board = create_board(20)

            placement = inductive_branch(g, A[0], A[0:4], None, None, (10,10), board.nodes) + [(A[0], (10,10))]
            print("Connecting branches")    
            placement = connect_branches(board, Graph(placement, []), [[i] for i in A[0:4]])
            print("Connecting rooms")
            placement = connect_necessary_rooms(board, placement, A[4:], A[:4])
            rooms = random_rooms.get_rooms(placement)
            break
        except Exception:
            print("Error, restarting")


    initialize_file(len(rooms), [str(i.id) for i in rooms if isinstance(i.prototype, Spawn) ][0])
    for i in rooms:
      transfer_to_file(i, scene, music)

   
    populate_rooms(rooms, scene)
    
    end = time.perf_counter()
    print(f"Map gen time: {end - start}")

def initialize_file(n: int, spawn: str) -> None:
    with open(FILENAME, "w") as fil:
        fil.write("".join([f"{i}##?" for i in range(n)]) + f"={spawn}")

def transfer_to_file(room: Room, scene: world.Map, music: music.Music):
    scene.load_room("Level/tile_map", room.segname, music)
    for n, i in enumerate(room.connections):
        if not i is None:
            if n == Orientation(0):
                scene.loading_zone.append(world.Loading_zone_cluster(0, str(i), 0, 0, 15, 1, 7.5, 15-2))
            elif n == Orientation(1):
                scene.loading_zone.append(world.Loading_zone_cluster(0, str(i), 15, 0, 1, 15, 2, 7.5))
            elif n == Orientation(2):
                scene.loading_zone.append(world.Loading_zone_cluster(0, str(i), 0, 15, 15, 1, 7.5, 2)) #wat
            else:
                scene.loading_zone.append(world.Loading_zone_cluster(0, str(i), 0, 0, 1, 15, 15-2, 7.5))
    scene.rotate(room.orientation)
    scene.save(FILENAME, str(room.id))

def populate_rooms(rooms: list[Room], scene: world.Map) -> None:
  actors = [i.populate((scene.change_state, scene.kill_actor)) for i in rooms]
  for n, i in enumerate(actors):
    for j in i:
      j.pos =vec2_add((7.5*tile,7.5*tile), rotate(rooms[n].orientation, vec2_add((-7.5*tile, -7.5*tile), j.pos)))
  actors = [(str(i.id), actors[n]) for n,i in enumerate(rooms)]

  scene.actors = dict(actors)


def travagg(s:Sequence[T], f:Callable[[T,T], T]) -> list[T]:
    a = []
    for n,i in enumerate(s[:len(s)-1]):
        a.append(f(i, s[n+1]))
    return a


def connect_branches(board: Graph[Pos], placement: Graph[tuple[Room_prototype, Pos]], disjoint_branches: list[list[Room_prototype]]) -> Graph[tuple[Room_prototype, Pos]] | None:
    get_pos = lambda x:[i[1] for i in placement.nodes if x is i[0]][0]
    get_room = lambda x:[i[0] for i in placement.nodes if x == i[1]][0]

    if len(disjoint_branches)==1:
        return placement

    pairs = list(chain(*[product(i,j) for i,j in pairwise(disjoint_branches)]))
    pairs_pos = list(map(lambda x:(get_pos(x[0]), get_pos(x[1])), pairs))
    paths =  list(starmap(dijkstra, 
                     starmap(lambda y,z: (Graph.without(board, [i for j,i in placement.nodes if not i == y and not i == z]), y, z),
                     pairs_pos)))
    shortest_path = min(list(filter(bool, paths)), key=len)
    if not shortest_path:
        return None
    placement.nodes = placement.nodes + list(map(lambda x: (Path(),x),  shortest_path[1:(len(shortest_path)-1)]))
    shortest_room_path = list(map(lambda x:(get_room(x), x), shortest_path))
    add_path = lambda x,y: ((x,y),(y,x))
    placement.edges = placement.edges + list(chain(*travagg(shortest_room_path, add_path)))
    
    start, end = tuple(shortest_room_path[::len(shortest_room_path)-1])
    start, end = start[0],  end[0]
    joined_graphs = [i for i in disjoint_branches if start in i or end in i]
    the_rest = [i for i in disjoint_branches if not (start in i or end in i)]
    the_rest.append(joined_graphs[0] + joined_graphs[1])

    return connect_branches(board, placement, the_rest)

def connect_necessary_rooms(board: Graph[Pos], placement: Graph[tuple[Room_prototype, Pos]], non_connected_rooms: list[Room_prototype], branches: list[Room_prototype]) -> Graph[tuple[Room_prototype, Pos]] | None:
    get_pos = lambda x:[i[1] for i in placement.nodes if x is i[0]][0]
    get_room = lambda x:[i[0] for i in placement.nodes if x == i[1]][0]
 

    if not non_connected_rooms:
        return placement

    pairs = product(branches, non_connected_rooms)
    pairs_pos = list(map(lambda x:(get_pos(x[0]), get_pos(x[1])), pairs))
    paths =  list(starmap(dijkstra, 
                     starmap(lambda y,z: (Graph.without(board, [i for j,i in placement.nodes if not i == y and not i == z]), y, z),
                     pairs_pos)))
    shortest_path = min(list(filter(bool, paths)), key=len)
    if not shortest_path:
        raise Exception("wierd connection problem")
    placement.nodes = placement.nodes + list(map(lambda x: (Path(),x),  shortest_path[1:(len(shortest_path)-1)]))
    shortest_room_path = list(map(lambda x:(get_room(x), x), shortest_path))
    add_path = lambda x,y: ((x,y),(y,x))
    placement.edges = placement.edges + list(chain(* travagg(shortest_room_path, add_path)))
    
    connected_room = shortest_room_path[len(shortest_room_path)-1]
    connected_room = connected_room[0]
    non_connected_rooms.remove(connected_room)
    print(connected_room)

    return connect_necessary_rooms(board, placement, non_connected_rooms, branches)




def vec2_add(x:tuple[int|float, int|float], y:tuple[int|float, int|float]) -> tuple[int|float, int|float]:
    return x[0]+y[0], x[1]+y[1]

def vec2_invert(x:tuple[int|float, int|float]) -> tuple[int|float, int|float]:
    return (-x[0], -x[1])
  
  
rotate90 = lambda x: (-x[1], x[0])
def rotate(n:int, x:tuple[int, int]) -> tuple[int, int]:
    if n:
        return rotate(n-1, rotate90(x))
    else:
        return x

def orientation_square(orientation: Orientation, pos: tuple[int, int]) -> tuple[int, int]:
    square_corner = vec2_add(rotate(orientation, (-1,2)), pos)
    return [vec2_add(i, square_corner) for i in product(range(2), range(2))]
 

def inductive_branch(g: Graph[Room_prototype], current_branch: Room_prototype, branches: list[Room_prototype], previous_branch: Room_prototype|None, previous_branch_orientation: Orientation|None, pos: Pos, square_map: list[Pos]) -> List[tuple[Room_prototype, Pos]]:
    neighbours = g.neighbours(current_branch)
    if previous_branch:
       neighbours.remove(previous_branch)
    if previous_branch_orientation is None: # can be zero
        orientations = list(range(4))
    else:
        orientations = list(range(4))
        orientations.remove((previous_branch_orientation+2) % 4)
    squares = [orientation_square(i, pos) for i in orientations]
    squares = list(map(lambda y:list(filter(lambda x: x in square_map, y)), squares))

    random.shuffle(neighbours)
    placement = []
    for n,i in enumerate(neighbours):
        pos = random.choice(squares[n])
        placement.append((i, pos))
        square_map.append(pos)
         
    if not previous_branch_orientation is None:
        squares.insert(previous_branch_orientation+2 % 4, (1000,1000)) #wtf fucking types dude lol 
 
    branches.remove(current_branch)
    active_branch_neighbours = [i for i in neighbours if i in branches]
    square_id_by_room_pos = lambda x: list(filter(lambda y:x in y[1], enumerate(squares)))[0][0]
    get_pos = lambda x:list(filter(lambda y:y[0]==x, placement))[0][1]
    return placement + reduce(lambda z,y: z+y, list(map(lambda x:inductive_branch(g, x, branches, current_branch, Orientation(square_id_by_room_pos(get_pos(x))), get_pos(x), square_map ), active_branch_neighbours )), [])
