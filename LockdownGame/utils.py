
from rlcard.games.base import Card

class EmptyCard(Card):
  def __init__(self):
    self.suit = "E"
    pass

  def __str__(self):
    return "EmptyCard"
  
# valid_rank = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
# valid_suit = ['S', 'H', 'D', 'C']

def get_card_from_id(card_id : int) -> Card:
  if (card_id == 56):
    return EmptyCard()
  elif not (0 <= card_id < 52):
    raise RuntimeError(f"Tried to get card {card_id}, which is not valid nor emptycard")
  
  rank_id = card_id % 13
  suit_id = card_id // 13
  suit_id, rank_id = divmod(card_id, 13)
  rank = Card.valid_rank[rank_id]
  suit = Card.valid_suit[suit_id]
  return Card(rank=rank, suit=suit)

_deck = [get_card_from_id(card_id) for card_id in range(52)] + [get_card_from_id(56)]

def get_card(card_id: int):
  if card_id == 56:
    return _deck[53] # FIXME this is ugly and awful and bad

  return _deck[card_id]


def get_card_id(card :Card) -> int:
  
  if isinstance(card, EmptyCard):
    return 56

  return Card.valid_suit.index(card.suit) + Card.valid_rank.index(card.rank) * 13



def get_deck() -> list[Card]:
  return _deck.copy()

