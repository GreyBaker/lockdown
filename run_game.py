import random
from pz_lockdown import env as LockdownEnv

env = LockdownEnv()
observations = env.reset()

done = {agent: False for agent in env.agents}
while not all(done.values()):
    actions = {
        agent: random.choice(range(env.action_spaces[agent].n)) for agent in env.agents if not done[agent]
    }
    observations, rewards, terminations, truncations, infos = env.step(actions)

    # Check if all agents are done
    done = {agent: terminations[agent] or truncations[agent] for agent in env.agents}

env.close()
