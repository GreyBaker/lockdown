import os; os.environ['PYTHONWARNINGS']='ignore::DeprecationWarnings'

from FormalEnvironment import LockupEnvRay

def test_lockup_env_minimal():
  # Initialize the environment
  env = LockupEnvRay()

  # Test reset
  obs, info = env.reset()
  assert isinstance(obs, dict), "Reset should return a dictionary of observations."
  print("Reset passed.")

  # Test step with random actions
  action_dict = {i: env.action_space.sample() for i in range(env.num_players)}
  obs, rewards, dones, infos = env.step(action_dict)
  
  assert isinstance(obs, dict), "Step should return a dictionary of observations."
  assert isinstance(rewards, dict), "Step should return a dictionary of rewards."
  assert isinstance(dones, dict), "Step should return a dictionary of done flags."
  assert "__all__" in dones, 'The "dones" dictionary must contain an "__all__" key.'
  
  print("Step passed.")

if __name__ == "__main__":
  test_lockup_env_minimal()
