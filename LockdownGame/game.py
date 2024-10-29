import numpy as np
from .action_event import *
from .judge import LockdownJudge
from .round import LockdownRound
from .player import LockdownPlayer

from .utils import EmptyCard

class LockdownGame:
  def __init__(self):
    self.np_random = None
    self.allow_step_back = False
    self.judge = LockdownJudge(game=self)
    self.actions : None | list[ActionEvent] = None
    self.round : None | LockdownRound = None
    self.num_players = 4

  def init_game(self):
    dealer_id = self.np_random.choice([0, 1, 2, 3])

    self.actions = []
    self.round = LockdownRound(dealer_id=dealer_id, np_random=self.np_random)
    
    for i in range(4):
      player = self.round.players[(dealer_id + 1 + i) % 4]
      self.round.dealer.deal_cards(player=player, num=13)

    current_player_id = self.round.current_player_id
    state = self.get_state(player_id=current_player_id)
    return state, current_player_id

  def step(self, action :ActionEvent):
    
    if isinstance(action, PlayCardAction):
      self.round.play_card(action)
    elif isinstance(action, PlayEmptyCardAction):
      self.round.play_empty_card()
    elif isinstance(action, ScoreAction):
      self.round.score_player(action)
    else:
      raise Exception(f"Unknown step action {action}")
    
    self.actions.append(action)
    next_player_id = self.round.current_player_id
    next_state = self.get_state(player_id=next_player_id)

    return next_state, next_player_id
  

  def step_back(self):
    raise NotImplementedError # Intentional
  
  def get_num_players(self):
    return 4
  
  def get_num_actions(self):
    return ActionEvent.get_num_actions()
  
  def get_player_id(self):
    return self.round.current_player_id
  
  def is_over(self):
    return self.round.is_over
  
  def get_current_player(self) -> LockdownPlayer | None:
    return self.round.get_current_player()
  
  def get_last_action(self) -> ActionEvent | None:
    return self.actions[-1] if self.actions and len(self.actions) > 0 else None
  
  def get_state(self, player_id :int):
    state = {}
    if not self.is_over():
      discard_pile = self.round.dealer.discard_pile
      # last_action = self.get_last_action()

      unknown_cards : list[Card] = []
      for i in range(4):
        if i == self.round.current_player_id:
          continue

        for card in self.round.players[i].hand:
          unknown_cards.append(card)
      state['player_id'] = self.round.current_player_id
      state['hand'] = [x.get_index() for x in self.round.players[self.round.current_player_id].hand]
      state['discard'] = [x.get_index() for x in discard_pile]
      state['unknown'] = [x.get_index() for x in unknown_cards if not isinstance(x, EmptyCard)]
      
      state['trick'] = {}
      for idx, card in enumerate(self.round.trick):
        state['trick'][idx] = card

    return state


  @staticmethod
  def decode_action(action_id) -> ActionEvent:
    return ActionEvent.decode_action(action_id=action_id)