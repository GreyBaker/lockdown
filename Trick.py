from Card import Card, Suit


class Trick:

  def __init__(self, start_player):
    assert 0 <= start_player <= 3

    self.plays : list[Card | None] = [None, None, None, None]
    self.lead = None
    self.turn = start_player
    self.start = start_player
    self.winner = None
    self.winner_lockdown = 0

  def makePlay(self, card : Card):

    # Check first hand
    if (all([i == None for i in self.plays])):
      self.lead = card.suit

    self.plays[self.turn] = card
    self.turn = (self.turn + 1) % 4

    if self.plays[self.turn] != None:
      self.determineWinnerAndLockdown()

  def determineWinnerAndLockdown(self):

    self.winner_lockdown = sum([(i.suit == Suit.CLUBS) for i in self.plays])

    self.winner = self.start
    for i in range(0, 4):
      if (self.plays[i].suit == self.lead and self.plays[i] > self.plays[self.winner]):
        self.winner = i


