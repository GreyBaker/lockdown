import numpy as np

from LockdownGame.lockdown_env import LockdownEnv
from LockdownGame.player import LockdownPlayer
from LockdownGame.game import LockdownGame


# from gymnasium.utils import EzPickle
from pettingzoo.utils import wrappers


def env(**kwargs):
  env = raw_env(**kwargs)
  env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
  env = wrappers.AssertOutOfBoundsWrapper(env)
  env = wrappers.OrderEnforcingWrapper(env)
  return env

from pettingzoo.classic.gin_rummy_v4 import raw_env as GRre # Reference

class raw_env(LockdownEnv):
  def __init__(self):

    LockdownEnv.__init__(self)
    self.env.set_agents() # TODO: need agent classes
    self.env.game.judge.scorer.get_payoff = self._get_payoff
    self.render_mode = None
    self.save_states = None

  def _get_payoff(self, player: LockdownPlayer, game : LockdownGame) -> float:
    # basically, 1 if trick taker 0 else 
    if (player.last_score == game.round.tricks_taken[player.get_player_id()]):
      payoff = 0
    else:
      payoff = self._trick_reward
      player.last_score = game.round.tricks_taken[player.get_player_id()]

    return payoff
  
  def observe(self, agent):
    obs = self.env.get_state(self._name_to_int(agent))
    observation = obs["obs"].astype(self._dtype)

    legal_moves = self.next_legal_moves
    action_mask = np.zeros(52, 'int8')
    for i in legal_moves:
      action_mask[i] = 1

    return {"observation":observation, "action_mask":action_mask}
  
  def step(self, action):
    super().step(action)

    if self.render_mode == 'human':
      self.render()

  def render(self):
    raise NotImplementedError # Temporarily intentional
  
  def close(self):
    pass


