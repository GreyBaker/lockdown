from LowAbstractionEnvironment import LockupGame
import numpy as np
from ray.rllib.env import MultiAgentEnv
from gymnasium import spaces

class LockupEnvRay(MultiAgentEnv):
    def __init__(self):
        super().__init__()
        self.game = LockupGame()
        self.num_players = 4

        self.agents = [i for i in range(self.num_players)]
        
        # MultiDiscrete?
        self.observation_space = spaces.Box(low=0, high=32, shape=(536,), dtype=np.int32) # This should be tightened
        self.action_space = spaces.Discrete(53)

        self.last_obs = {}
        self.last_rew = {}
        self.last_done = {}
        self.last_info = {}

        self.i = 0

        # self.observation_spaces = {player : spaces.Box(low=0, high=1, shape=(488,), dtype=np.int32) for player in self.agents}
        # self.action_spaces = {player : spaces.Discrete(53) for player in self.agents}

        # self.observation_space = spaces.Dict(self.observation_spaces)
        # self.action_space = spaces.Dict(self.action_spaces)
        print("Init complete")
    
    def render(self):
        print("start render")
        # Do a lil render
        print()
        print(self.game.player_scores)
        for i in range(4):
            print(i, self.game.str_player_hand(i), end=' || ')
        print()


    def reset(self, seed=None, options=None):
        print("start reset")
        self.i = self.game._deal_round_and_state_first_player()
        single_obs = self.game.present_observation_space(self.i)
        info = {}
        
        print("on reset", type(single_obs), single_obs.shape)
        # return single_obs, info
        with open("out.txt", 'w') as f:
            f.write(str(single_obs))
        return {self.i : single_obs}, info
        # return obs
    
    def step(self, action_dict):
        print("start step")
        # action = action_dict[player_id]
        self.i = self.game.make_play_and_state_next_player(self.i, action_dict[self.i])

        obs = self._get_obs()
        print("?????????", obs[0].shape)
        rewards = self._get_rewards()
        dones = self._get_dones()
        infos = self._get_infos()

        print("RAH IMA RETURN ON STEP !!!")
        return (
            {self.i : self.game.present_observation_space(self.i)},
            {self.i : self.game.player_scores[self.i]},
            {"__all__": False},
            # {"__all__": False},
            {},
        )

        return obs, rewards, dones, infos

    def _get_obs(self):

        return {i: self.game.present_observation_space(i) for i in range(self.num_players)}

    def _get_rewards(self):
        # ???
        return {i: self.game.player_scores[i] for i in range(self.num_players)}

    def _get_dones(self): # ??? This may not be necessary tbh
        game_over = np.any(self.game.player_scores >= 20)
        dones = {i: game_over for i in range(self.num_players)}
        dones["__all__"] = game_over
        return dones

    def _get_infos(self):
        return {i: {} for i in range(self.num_players)}

    def get_agent_ids(self):
        return self.agents

    def get_action_mask(self):
        return {i: self.game.present_action_space(i) for i in range(self.num_players)}



from ray.tune.registry import register_env

def env_creator(config):
    return LockupEnvRay()

register_env("lockup", env_creator)