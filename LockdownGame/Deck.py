import random
from .Card import Card, Suit

NUM_SUITS = len(Suit)
MIN_RANK = 2
MAX_RANK = 14

class Deck:
  def __init__(self):
    self.deck = []
    self.reset()

  def reset(self):
    for suit in range(0, NUM_SUITS):
      for rank in range(MIN_RANK, MAX_RANK + 1):
        self.deck.append(Card(rank, suit))
    
  def __str__(self):
    return str(self.deck)
  
  def shuffle(self):
    random.shuffle(self.deck, random.random)

  def deal(self):
    return self.deck.pop(0)
  
  def size(self):
    return len(self.deck)
  
  