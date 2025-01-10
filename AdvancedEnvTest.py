import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from FormalEnvironment import LockupEnvRay  # Assuming your environment is defined here
import os

# !!!

# Define a simple neural network for action prediction
class TwinLayerNN(nn.Module):
  def __init__(self, input_size, output_size):
    super().__init__()
    self.linear_stack = nn.Sequential(
      nn.Linear(input_size, 256),
      nn.ReLU(),
      nn.Linear(256, 256),
      nn.ReLU(),
      nn.Linear(256, output_size),
      nn.LogSoftmax(dim=0)
    )

  def forward(self, x):
    x = self.linear_stack(x)
    return x

# Initialize the environment
env = LockupEnvRay()
obs_space_shape = env.observation_space.shape[0]
action_space_size = env.action_space.n

# !!! it is highkey faster at this scale on my cpu, but i be using my cpu
device = torch.device('cuda')
# device = torch.device('cpu')

# Initialize the neural network, optimizer, and loss function
model = TwinLayerNN(input_size=obs_space_shape, output_size=action_space_size).to(device)
optimizer = optim.Adam(model.parameters(), lr=0.001)
# loss_fn = nn.CrossEntropyLoss()  # For discrete action spaces



# Training loop (basic interaction)
def train(env : LockupEnvRay, model : nn.Module, episodes=10):
  for episode in range(episodes):
    obs_dict, _ = env.reset()
    done = False
    rewards = None

    while not done:
      initial_scores = env.game.player_scores
      saved_forward_log_probs : list[None | torch.Tensor] = [None, None, None, None]

      losses = [0]


      for _ in range(4):
        # print(saved_forward_log_probs)
        # Prepare observations for the model
        player = [i for i in obs_dict.keys()][0]
        # print("Player:", player)
        obs_array = np.array(obs_dict[player])  # Convert dict to array of observations
        obs_tensor = torch.tensor(obs_array, dtype=torch.float, device=device)

        action_mask = env.game.present_action_space(player)

        action_logits = model.forward(obs_tensor) # ? .clone()
        actions = action_logits.flatten()  # Choose actions greedily
        action_dist = torch.distributions.Categorical(actions)
        action = action_dist.sample()

        if action_mask[action.detach().to(device='cpu').item()] == 0:
          # print('nroom')
          
          # Train against illegal moves
          log_prob = action_dist.log_prob(action)
          loss = 20 * log_prob
          # losses.append(losses[-1] + loss)

          loss.backward(retain_graph = True)
          
          # print("CRSSH")

          indices = np.where(action_mask == 1)[0]

          randomized_action = np.random.choice(indices)
          action_dict = {player : randomized_action}

        else:

        
          # print('skrrt')
          # print(saved_forward_log_probs)

          assert saved_forward_log_probs[player] is None
          log_prob = action_dist.log_prob(action)
          saved_forward_log_probs[player] = log_prob

          # print(actions, action)

          # Create action dictionary
          action_dict = {player : action.detach().to(device='cpu').numpy()}

        # Step through the environment
        obs_dict, rewards, dones, infos = env.step(action_dict)

        # Check if the episode has ended
        done = dones["__all__"]

      d_scores = env.game.player_scores - initial_scores
      optimizer.zero_grad()

      # print('prrt')
      # print(saved_forward_log_probs)
      for player, log_prob_tensor in enumerate(saved_forward_log_probs):
        if log_prob_tensor == None:
          continue

        # print('tensr', log_prob_tensor)

        if d_scores[player] == 0:
          loss = .25 * log_prob_tensor

          losses.append(losses[-1] + loss)

        else:
          loss = -1 * log_prob_tensor

          

          losses.append(loss + losses[-1])

        loss.backward(retain_graph=(player != 3))

      batch_loss = losses[-1]
      
      print('\r', episode, env.game.player_scores, batch_loss, end = '')

      
      # batch_loss.backward()
      optimizer.step()


# Run the training loop
if (os.path.isfile('TwinLayerNN.pt')):
  model = torch.load('TwinLayerNN.pt', weights_only=False)
for i in range(100):
  train(env, model, episodes=100)
  torch.save(model, 'TwinLayerNN.pt')