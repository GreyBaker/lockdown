
from rlcard.games.base import Card
from .utils import get_card_id, get_card

class ActionEvent(object):

  def __init__(self, action_id: int):
    self.action_id = action_id

  def __eq__(self, other):
    result = False
    if isinstance(other, ActionEvent):
      result = self.action_id == other.action_id
    return result
  
  @staticmethod
  def get_num_actions():
    return 53 # First 0-51 are cards, 52-55 are scoring
  
  @staticmethod
  def decode_action(action_id) -> 'ActionEvent':
    if action_id in range(0, 52):
      card = get_card(card_id=action_id)
      action_event = PlayCardAction(card=card)
    elif action_id in range(52, 56):
      action_event = ScoreAction(player_id=action_id-52)
    elif action_id == 56:
      action_event = PlayEmptyCardAction(action_id=action_id)
    else:
      raise Exception(f"Unknown action id in decode action: {action_id}")
    return action_event


class PlayCardAction(ActionEvent):
  def __init__(self, card: Card):
    card_id = get_card_id(card)
    super().__init__(action_id=card_id)
    self.card = card

  def __str__(self):
    return f"play {str(self.card)}"
  

class ScoreAction(ActionEvent):
  def __init__(self, player_id :int):
    self.player_id = player_id
    super().__init__(action_id=player_id+52)

  def __str__(self):
    return f"Scoring player {self.player_id}"
  
class PlayEmptyCardAction(ActionEvent):
  def __init__(self, action_id : int):
    super().__init__(action_id=action_id)

  def __str__(self):
    return f"playing empty card"