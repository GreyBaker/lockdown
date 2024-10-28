from .player import LockdownPlayer
from .action_event import *

class LockdownMove(object):
  pass


class PlayerMove(LockdownMove):

  def __init__(self, player : LockdownPlayer, action : ActionEvent):
    super().__init__()
    self.player = player
    self.action = action

class DealHandMove(LockdownMove):
  def __init__(self, player_dealing: LockdownPlayer, shuffled_deck: list[Card]):
    super().__init__()
    self.player_dealing = player_dealing
    self.shuffled_deck = shuffled_deck

  def __str__(self):
    shuffled_deck_text = " ".join([str(card) for card in self.shuffled_deck])
    return "{} deal shuffled_deck=[{}]".format(self.player_dealing, shuffled_deck_text)

class ScoreMove(LockdownMove):
  def __init__(self, player : LockdownPlayer, action : ActionEvent, score : int):
    self.player = player
    self.action = action
    self.score = score

  
  def __str__(self):
    return f"Scoring for {self.player} gets {self.score}"
  
class PlayCardMove(LockdownMove):

  def __init__(self, player : LockdownPlayer, action : PlayCardAction):
    super().__init__()
    self.player = player
    self.action = action

  def __str__(self):
    return f"Player {self.player} plays card with {self.action}"
