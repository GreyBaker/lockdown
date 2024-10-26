from .Card import Suit, Card
from random import randint

FULL_HAND_SIZE = 13

class Hand:
  def __init__(self):

    self.hand = [[], [], [], []]

  def __len__(self):
    return sum([len(i) for i in self.hand])
  
  def addCard(self, card : Card):

    self.hand[card.rank].append(card)

    self.hand[card.rank].sort()

    if len(self) == FULL_HAND_SIZE:
      for suit in self.hand:
        suit.sort()

  def popRandomCard(self):

    selection = randint(0, len(self) - 1)

    for suit in self.hand:
      if (selection < len(suit)):
        return self.playCard(suit[selection], True)
      
      selection -= len(suit)
  
  def playCard(self, card :Card, isRandomCard : bool):

    assert (self.canPlayCard(card) or isRandomCard)

    self.hand[card.suit].remove(card)

    return card


  def canPlayCard(self, card : Card, lead_suit : None | int, jqk_played = (False, False, False)):

    # Must have the card
    if (card not in self.hand[card.rank]):
      return False

    # Can only play club on lead when holding no other suits
    if (lead_suit == None and card.suit == Suit.CLUB and len(self.hand[Suit.CLUB]) != len(self)):
      return False
    
    # otherwise any lead is valid
    elif (lead_suit == None):
      return True

    # Can always play club jqk on match
    elif (card.suit == Suit.CLUB and jqk_played[card.rank - 11]):
      return True

    # Can only play lead suit if held
    elif (len(self.hand[lead_suit]) > 0):
      return card.rank == lead_suit

    # Can play anything
    else:
      return True
    
  
  def __str__(self):
    return str(self.hand)
  
  def getSimplifiedHand(self) -> list[Card]:

    combined_list = []

    for suit_list in self.hand:
      combined_list += suit_list

    return combined_list
  
  def info(self):
    return [card.info() for card in self.getSimplifiedHand()]