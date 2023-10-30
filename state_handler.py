import enum
import src.world_handler as world_handler
import src.gameover as gameover
import src.title as title
import src.create_map as create_map
import src.state as st


class previous:
  state = None

def state_handling(state, scene, framecount, event_list, music) -> st.State:
  if state == st.State.OVERWORLD:
    return world_handler.overworld_handler(scene, framecount, event_list, music)
  elif state == st.State.TITLE:
    if previous.state != state:
      title.startup(music)
      return title.title_handler(scene, framecount, event_list, music)
    return title.title_handler(scene, framecount, event_list, music)
  elif state == st.State.GAMEOVER:
    if previous.state != state:
      gameover.startup(music)
      return gameover.gameover_handler(scene, framecount, event_list)
    return gameover.gameover_handler(scene, framecount, event_list)
  elif state == st.State.MAP_GEN:
    return create_map.mapgen_handler(music)
