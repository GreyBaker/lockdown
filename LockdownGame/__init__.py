from .Lockdown import *

from gymnasium.envs.registration import register

register(
    id='Lockdown_Game-v0',
    entry_point='LockdownGame.Lockdown:LockdownEnv',
)