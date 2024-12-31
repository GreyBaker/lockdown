from LowAbstractionEnvironment import LockupGame
import numpy as np
from ray.rllib.env import MultiAgentEnv
from gymnasium import spaces

class LockupEnvRay(MultiAgentEnv):
    def __init__(self, config=None):
        super().__init__()
        self.game = LockupGame()
        self.num_players = 4
        self.agents = [f"player_{i}" for i in range(self.num_players)]
        self.observation_space = spaces.Box(low=0, high=1, shape=(439,), dtype=np.int32)
        self.action_space = spaces.Discrete(53)

    def reset(self):
        self.game._deal_round_and_state_first_player()
        return self._get_obs()

    def step(self, action_dict):
        player_id = self.game.next_player
        action = action_dict[f"player_{player_id}"]
        next_player = self.game.make_play_and_state_next_player(player_id, action)

        obs = self._get_obs()
        rewards = self._get_rewards()
        dones = self._get_dones()
        infos = self._get_infos()

        return obs, rewards, dones, infos

    def _get_obs(self):
        return {f"player_{i}": self.game.present_observation_space(i) for i in range(self.num_players)}

    def _get_rewards(self):
        # ???
        return {f"player_{i}": self.game.player_scores[i] for i in range(self.num_players)}
        # return {f"player_{i}" : int(self.game.trick_winner == i) for i in range(self.num_players)}

    def _get_dones(self): # ??? This may not be necessary tbh
        game_over = np.any(self.game.player_scores >= 20)
        dones = {f"player_{i}": game_over for i in range(self.num_players)}
        dones["__all__"] = game_over
        return dones

    def _get_infos(self):
        return {f"player_{i}": {} for i in range(self.num_players)}

    def get_agent_ids(self):
        return self.agents

    def get_action_mask(self):
        return {f"player_{i}": self.game.present_action_space(i) for i in range(self.num_players)}

from ray.tune.registry import register_env

def env_creator(config):
    return LockupEnvRay(config)

register_env("lockup", env_creator)