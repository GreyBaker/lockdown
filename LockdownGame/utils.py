
from rlcard.games.base import Card
import numpy as np

class EmptyCard(Card):
  def __init__(self):
    super().__init__("E", "0")

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


def get_card_id(card : str | Card) -> int:

  if isinstance(card, str):
    suit = card[0]
    rank = card[1]
  else:
    suit = card.suit
    rank = card.rank
  
  if isinstance(card, EmptyCard) or card == "EmptyCard":
    return 56

  return Card.valid_suit.index(suit) * 13 + Card.valid_rank.index(rank)



def get_deck() -> list[Card]:
  return _deck.copy()


def encode_cards(cards : list[Card]) -> np.ndarray:
  plane = np.zeros(52, dtype=int)
  for card in (cards if cards is not None else []):
    if isinstance(card, EmptyCard): # ??? may need to include empty card in trick info sometimes
      continue
      
    card_id = get_card_id(card) # TODO: complete
    if card_id == 56:
      continue

    plane[card_id] = 1
  return plane