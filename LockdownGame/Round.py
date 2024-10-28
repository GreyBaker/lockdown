import numpy as np
from .action_event import *
from .judge import LockdownJudge
from .round import LockdownRound
from .player import LockdownPlayer
from .dealer import LockdownDealer
from .move import *
from .utils import EmptyCard

# Really only built to handle one round right now
class LockdownRound:
  
  def __init__(self, dealer_id : int, np_random):
    self.np_random = np_random
    self.dealer_id = dealer_id
    self.dealer = LockdownDealer(self.np_random)
    self.players = [LockdownPlayer(player_id=i, np_random=self.np_random) for i in range(4)]
    self.current_player_id = dealer_id

    self.trick : list[None | Card] = [None, None, None, None]
    self.tricks_taken = [0, 0, 0, 0] # in round

    self.is_over = False
    self.going_out_action = None
    self.going_out_player_id = None
    self.move_sheet : list[LockdownMove] = []
    player_dealing = self.players[dealer_id]
    shuffled_deck = self.dealer.shuffled_deck
    self.move_sheet.append(DealHandMove(player_dealing=player_dealing, shuffled_deck=shuffled_deck))

  def get_current_player(self) -> LockdownPlayer | None:
    current_player_id = self.current_player_id
    return None if current_player_id is None else self.players[current_player_id]
  
  # Need to consider finish trick and score round
  def play_card(self, action : PlayCardAction):
    current_player = self.players[self.current_player_id]

    # Pop card from player hand
    self.move_sheet.append(PlayCardMove(current_player, action))

    card = current_player.play_card(card=card)
    self.dealer.discard_pile.append(card)
    self.current_player_id = (self.current_player_id + 1) % 4

    if self._trick_isFull():
      self._trick_score()
      self.trick = [None, None, None, None]

  def play_empty_card(self, action : PlayEmptyCardAction):
    current_player = self.players[self.current_player_id]

    # Pop card from player hand
    self.move_sheet.append(PlayCardMove(current_player, action))

    card = current_player.play_empty_card()
    self.dealer.discard_pile.append(card)
    self.current_player_id = (self.current_player_id + 1) % 4

    if self._trick_isFull():
      self._trick_score()
      self.trick = [None, None, None, None]
      

  def _trick_isFull(self):
    return all([play is not None for play in self.trick])
  
  def _trick_score(self):

    RANKS_IN_ORDER = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    if all([isinstance(self.trick[i], EmptyCard) for i in range(4)]):
      self.tricks_taken[self.dealer_id] += 1
      return

    lead_suit = None
    best_id_so_far = -1

    for i in range(4):
      relevant_player = (self.dealer_id + i) % 4
      if isinstance(self.trick[relevant_player], EmptyCard):
        continue

      if (lead_suit is None):
        lead_suit = self.trick[relevant_player].suit
        best_id_so_far = relevant_player
        continue

      if RANKS_IN_ORDER.index(self.trick[relevant_player].suit) > RANKS_IN_ORDER.index(self.trick[relevant_player].suit):
        best_id_so_far = relevant_player
    
    lockdown = sum([card.suit == "C" for card in self.trick])

    self.players[best_id_so_far].lockdown_time += lockdown
    self.tricks_taken[best_id_so_far] += 1
    self.current_player_id = best_id_so_far

  def score_player(self, action : ScoreAction):
    
    if self.current_player_id != action.player_id:
      raise RuntimeError("Player to be scored does not match current player")

    current_player = self.players[action.player_id]
    self.move_sheet.append(ScoreMove(player=current_player, action=action, score=self.tricks_taken[current_player.player_id]))
    self.current_player_id = (self.current_player_id + 1) % 4 # Mod should be unnecessary

    if action.player_id == 3:
      self.is_over = True
    




