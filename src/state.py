import enum # big file

class State(enum.Enum):
  OVERWORLD = enum.auto()
  COMBAT = enum.auto()
  NPC_DIALOG = enum.auto()
  TITLE = enum.auto()
  GAMEOVER = enum.auto()
