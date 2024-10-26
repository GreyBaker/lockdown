
from enum import Enum


class Suit(Enum):
  CLUB = 0
  SPADE = 1
  DIAMOND = 2
  HEART = 3

  def __len__():
    return 4



class Card:
  def __init__(self, rank, suit):
    self.rank : int = rank
    self.suit : int = suit

  def __eq__(self, other):
    return type(other) == Card and (self.rank == other.rank and self.suit == other.suit)
  
  # These for sorting purposes in hand only, hand variation is arbitrary
  def __gt__(self, other):
    assert type(other) == Card
    return self.suit < other.suit or self.rank > other.rank
  def __lt__(self, other):
    assert type(other) == Card
    return self.suit < other.suit or self.rank < other.rank

  def __str__(self):
    return str(self.rank).zfill(2) + "|" + str(self.suit)
  
  def info(self):
    return {'rank': self.rank, 'suit':self.suit}



