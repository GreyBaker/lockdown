

from rlcard.games.base import Card
from .player import LockdownPlayer
from .utils import get_deck

class LockdownDealer:
  def __init__(self, np_random):
    self.np_random = np_random
    self.discard_pile : list[Card] = []
    self.shuffled_deck = get_deck()
    self.deck_to_deal = self.shuffled_deck.copy()
    
  def deal_cards(self, player: LockdownPlayer, num: int):
    for _ in range(num):
      player.hand.append(self.deck_to_deal.pop())
