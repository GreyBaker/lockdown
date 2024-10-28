from typing import Callable
from .player import LockdownPlayer
# from .game import LockdownGame
from .action_event import *
from .utils import EmptyCard

class LockdownScorer:
  def __init__(self, get_payoff  = None): # Payoff Callable[[LockdownPlayer, 'LockdownGame'], int | float]
    self.get_payoff = get_payoff if get_payoff else get_payoff_v0

  def get_payoffs(self, game):
    return [self.get_payoff(player=player, game=game) for player in game.round.players]

def get_payoff_v0(player : LockdownPlayer, game) -> float:

  return game.round.tricks_taken[player.get_player_id()]
  


class LockdownJudge:
  

  def __init__(self, game):
    self.game = game
    self.scorer = LockdownScorer()

  def get_legal_actions(self) -> list[ActionEvent]:
    legal_actions : list[ActionEvent] = []

    last_action = self.game.get_last_action()

    if last_action is None or (isinstance(last_action, PlayCardAction) and all([len(player.hand) == 0 for player in self.game.round.players])):
      current_player = self.game.get_current_player()
      hand = current_player.hand
      trick_so_far = self.game.round.trick

      if current_player.lockdown_time > 0:
        legal_actions = [PlayEmptyCardAction()]
        return legal_actions

      # Select valid cards to play here
      lead_suit = None
      for i in range(4):
        relevant_player = (self.game.round.dealer_id + i) % 4
        if not(trick_so_far[i] is None or isinstance(trick_so_far[i], EmptyCard)):
          lead_suit = trick_so_far[i].suit
          break


      # Club Lead case
      if lead_suit == None and all([card.suit == 'C' for card in hand]):
        for card in hand:
          legal_actions += [PlayCardAction(card=card)]
        return legal_actions

      # Nonclub Lead case
      if lead_suit is None:
        for card in hand:
          if card.suit == 'C':
            continue
          legal_actions += [PlayCardAction(card=card)]
        return legal_actions

      # Follow cases:
      # On suit
      if any([card.suit == lead_suit for card in hand]):
        for card in hand:
          if card.suit != lead_suit:
            continue
          legal_actions += [PlayCardAction(card=card)]

      # Off suit
      else:
        for card in hand:
          legal_actions += [PlayCardAction(card=card)]

      # Face Clubs
      for test_rank in ['J', 'Q', 'K']:
        test_card = Card('C', test_rank)
        if test_card in hand and any([card.rank == 'J' for card in hand]) and not PlayCardAction(card=test_card) in legal_actions:
          legal_actions += [PlayCardAction(card=test_card)]


    elif isinstance(last_action, PlayCardAction): # but, implicitly, all hands are 0
      legal_actions = [ScoreAction(player_id=0)]
    elif isinstance(last_action, ScoreAction):
      if last_action.player_id == 3:
        return legal_actions
      
      legal_actions = [ScoreAction(player_id=last_action.player_id + 1)]
      
    else:
      raise Exception(f"get legal actions, unknown action {last_action}")


    return legal_actions