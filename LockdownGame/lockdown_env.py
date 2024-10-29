import numpy as np

from collections import OrderedDict
from pettingzoo import AECEnv
from gymnasium import spaces

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
    # self.game.configure(_game_config) # ???
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
      current_player = self.game.get_current_player()
      dict_state = self.game.get_state(current_player.get_player_id())
      own = self._utils.encode_cards(dict_state['hand'])
      discard = self._utils.encode_cards(dict_state['discard'])
      # Trick goes around the table starting at the player to the left
      trick_hands = []
      for i in range(1, 4):
        trick_player_id = (current_player.player_id + i) % 4
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
  # from pettingzoo.classic.rlcard_envs.rlcard_base import RLCardBase # reference
  
  def __init__(self):
    super().__init__()

    self.name = 'lockdown'
    self.env = FundamentalLockdownEnv(config={'seed':None})
    self.num_players = self.env.num_players

    self.screen = None
    if not hasattr(self, 'agents'):
      self.agents = [f'player_{i}' for i in range(self.num_players)]
    self.possible_agents = self.agents[:]

    dtype = self.env.reset()[0]['obs'].dtype
    if dtype == np.dtype(np.int64):
      self._dtype = np.dtype(np.int8)
    elif dtype == np.dtype(np.float64):
      self._dtype = np.dtype(np.float32)
    else:
      self._dtype = dtype

    obs_shape = (6, 52)
    self.observation_spaces = self._convert_to_dict(
      [
        spaces.Dict(
          {
            'observation': spaces.Box(
              low=0.0, high=1.0, shape=obs_shape, dtype=self._dtype
            ),
            'action_mask': spaces.Box(
              low=0, high=1, shape=(self.env.num_actions,), dtype=np.int8
            )
          }
        )
        for _ in range(self.num_agents)
      ]
    )
    self.action_spaces = self._convert_to_dict(
      [spaces.Discrete(self.env.num_actions) for _ in range(self.num_agents)]
    )

  def observation_space(self, agent):
    return self.observation_spaces[agent]
  
  def action_space(self, agent):
    return self.action_spaces[agent]
  
  def _seed(self, seed=None):
    self.env = FundamentalLockdownEnv(config={'seed':seed})

  def _scale_rewards(self, reward):
    return reward
  
  def _int_to_name(self, ind):
    return self.possible_agents[ind]
  
  def _name_to_int(self, name):
    return self.possible_agents.index(name)
  
  def _convert_to_dict(self, list_of_list):
    return dict(zip(self.possible_agents, list_of_list))
  
  def observe(self, agent):
    obs = self.env.get_state(self._name_to_int(agent))
    observation = obs['obs'].astype(self._dtype)

    legal_moves = self.next_legal_moves
    action_mask = np.zeros(self.env.num_actions, 'int8')
    for i in legal_moves:
      action_mask[i] = 1
    
    return {'observation':observation, 'action_mask':action_mask}
  
  def step(self, action):
    if (self.terminations[self.agent_selection] or self.truncations[self.agent_selection]):
      return self._was_dead_step(action)
    obs, next_player_id = self.env.step(action)
    next_player = self._int_to_name(next_player_id)
    self._last_obs = self.observe(self.agent_selection)
    if self.env.is_over():
      self.rewards = self._convert_to_dict(
        self._scale_rewards(self.env.get_payoffs())
      )
      self.next_legal_moves = []
      self.terminations = self._convert_to_dict(
        [True for _ in range(self.num_agents)]
      )
      self.truncations = self._convert_to_dict(
        [False for _ in range(self.num_agents)]
      )
    else:
      self.next_legal_moves = obs['legal_actions']
    self._cumulative_rewards[self.agent_selection] = 0
    self.agent_selection = next_player
    self._accumulate_rewards()
    self._deads_step_first()
    
  
  def reset(self, seed=None, options=None):
    if seed is not None:
      self._seed(seed=seed)
    obs, player_id = self.env.reset()
    self.agents = self.possible_agents[:]
    self.agent_selection = self._int_to_name(player_id)
    self.rewards = self._convert_to_dict([0 for _ in range(self.num_agents)])
    self._cumulative_rewards = self._convert_to_dict(
      [0 for _ in range(self.num_agents)]
    )
    self.terminations = self._convert_to_dict(
      [False for _ in range(self.num_agents)]
    )
    self.truncations = self._convert_to_dict(
      [False for _ in range(self.num_agents)]
    )
    self.infos = self._convert_to_dict(
      [{} for _ in range(self.num_agents)]
    )
    self.next_legal_moves = list(sorted(obs['legal_actions']))
    self._last_obs = obs['obs']

  def render(self):
    raise NotImplementedError("No render built for LockdownEnv")
  
  def close(self):
    pass
  
  




