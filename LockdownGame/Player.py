import numpy as np
from rlcard.games.base import Card
from .utils import EmptyCard


class LockdownPlayer:
  def __init__(self, id, np_random :np.random):

    self.player_id = id
    self.np_random = np_random
    self.hand : list[Card] = []

    self.lockdown_time = 0

    self.last_score = 0
    # self.cards_seen = [False for _ in range(52)] 

  def get_player_id(self) -> int:
    return self.player_id
  
  def play_card(self, card :Card) -> Card:
    self.hand.remove(card)

    return card

  def play_empty_card(self):
    # Eventually, handle the edge case of no-one can play a card

    self.hand.pop(self.np_random.randint(0, len(self.hand) - 1))
    self.lockdown_time -= 1

    return EmptyCard()
    

  def __str__(self):
    return str(self.player_id)