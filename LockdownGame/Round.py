from random import randint
from .Deck import Deck
from .Trick import Trick

class Round:
  def __init__(self):
    self.tricksWon = [0, 0, 0, 0]
    self.roundComplete = False

    self.starter = randint(0, 3)
    self.current_lead = self.starter

    self.deck = Deck()

    self.locktimes = [0, 0, 0, 0]

    self.reset()
    

  def reset(self):
    self.tricksWon = [0, 0, 0, 0]
    self.roundComplete = False

    self.deck.reset()
    self.deck.shuffle()

    self.starter = (self.starter + 1) % 4
    self.current_lead = self.starter

    self.locktimes = [0, 0, 0, 0]

    self.startTrick()

  def endTrick(self):

    self.locktimes[self.trick.winner] += self.trick.winner_lockdown
    self.tricksWon[self.trick.winner] += 1

    for idx, val in enumerate(self.locktimes):
      if (val > 0):
        self.locktimes[idx] -= 1

    for shift in range(4):
      candidate = (self.trick.winner + shift) % 4
      if self.locktimes[candidate] == 0:
        self.current_lead = candidate

    if sum(self.tricksWon) == 13:
      self.roundComplete = True

  def startTrick(self):
    self.trick = Trick(self.current_lead)

    
