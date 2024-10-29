import numpy as np

from collections import OrderedDict
from pettingzoo import AECEnv

from rlcard.utils.seeding import np_random


class FundamentalLockdownEnv(object): 
  def __init__(self, config):
    from LockdownGame.game import LockdownGame
    from LockdownGame.move import ScoreMove
    import LockdownGame.utils as utils

    self._utils = utils
    self._ScoreMove = ScoreMove
    self.name = 'lockdown'
    self.game = LockdownGame()


    self.action_recorder = []
    self.game.configure(_game_config) # ???
    self.num_players = self.game.get_num_players()
    self.num_actions = self.game.get_num_actions()
    self.timestep = 0
    self.seed(config['seed'])
    self.state_shape = [[6, 52] for _ in range(self.num_players)]
    self.action_shape = [None for _ in range(self.num_players)]

  def reset(self):
    # base
    state, player_id = self.game.init_game()
    self.action_recorder = []
    return self._extract_state(state), player_id

  def step(self, action, raw_action=False):
    # base
    if not raw_action:
      action = self._decode_action(action)
    
    self.timestep += 1
    self.action_recorder.append((self.get_player_id(), action))
    next_state, player_id = self.game.step(action)
    return self._extract_state(next_state), player_id

  def step_back(self):
    raise NotImplementedError("No step back for BaseLockdownEnv")

  def set_agents(self, agents):
    self.agents = agents

  def run(self, is_training=False):
    trajectories = [[] for _ in range(self.num_players)] # players, transitions, content
    state, player_id = self.reset()

    trajectories[player_id].append(state)
    while not self.is_over():
      # Agent play
      if not is_training:
        action, _ = self.agents[player_id].eval_step(state)
      else:
        action = self.agents[player_id].step(state)

      # Environment
      next_state, next_player_id = self.step(action, self.agents[player_id].use_raw)
      trajectories[player_id].append(action)

      state = next_state
      player_id = next_player_id

      if not self.game.is_over():
        trajectories[player_id].append(state)

    for player_id in range(self.num_players):
      state = self.get_state(player_id)
      trajectories[player_id].append(state)

    payoffs = self.get_payoffs()
    
    return trajectories, payoffs

  def is_over(self):
    return self.game.is_over()

  def get_player_id(self):
    return self.game.get_player_id()

  def get_state(self, player_id):
    return self._extract_state(self.game.get_state(player_id))

  def get_payoffs(self):
    # is_game_complete = False
    # if self.game.round:
    #   move_sheet = self.game.round.move_sheet
    #   if move_sheet and isinstance(move_sheet[-1], self._ScoreMove) and self._ScoreMove.player == 3:
    #     is_game_complete = True
    # May need to give payoffs as 0 list if game not ended

    payoffs = self.game.judge.scorer.get_payoffs(game=self.game)

    return np.array(payoffs)

  def get_perfect_information(self):
    raise NotImplementedError # Not in reference?

  def get_action_feature(self, action):
    feature = np.zeros(self.num_actions, dtype=np.int8)
    feature[action] = 1
    return feature

  def seed(self, seed=None):
    self.np_random, seed = np_random(seed)
    self.game.np_random = self.np_random
    return seed

  def _extract_state(self, state): # State itself is deprecated
    if self.game.is_over():
      obs = np.array([self._utils.encode_cards([]) for _ in range(6)])
      extracted_state = {'obs': obs, 'legal_actions':self._get_legal_actions()}
      extracted_state['raw_legal_actions'] = list(self._get_legal_actions().keys())
      extracted_state['raw_obs'] = obs
    else:
      dict_state = self.game.get_state()
      own = self._utils.encode_cards(dict_state['hand'])
      discard = self._utils.encode_cards(dict_state['discard'])
      # Trick goes around the table starting at the player to the left
      trick_hands = []
      for i in range(1, 4):
        trick_player_id = (self.game.get_current_player().player_id + i) % 4
        trick_hands.append(self._utils.encode_cards(dict_state['trick'][trick_player_id]))
      unknown = self._utils.encode_cards(dict_state['unknown'])
      obs = np.array([own, discard, trick_hands[0], trick_hands[1], trick_hands[2], unknown])
      extracted_state = {'obs':obs, 'legal_actions':self._get_legal_actions(), 'raw_legal_actions':list(self._get_legal_actions().keys())}
      extracted_state['raw_obs'] = obs

    return extracted_state
  
  def _decode_action(self, action_id) -> str:
    return self.game.decode_action(action_id=action_id)
    
  def _get_legal_actions(self):
    legal_actions = self.game.judge.get_legal_actions()
    legal_actions_ids = {action_event.action_id : None for action_event in legal_actions}
    return OrderedDict(legal_actions_ids)




class LockdownEnv(AECEnv):
  from pettingzoo.classic.rlcard_envs.rlcard_base import RLCardBase # reference
  
  raise NotImplementedError # TODO
  
  




