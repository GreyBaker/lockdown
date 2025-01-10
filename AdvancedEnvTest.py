import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from FormalEnvironment import LockupEnvRay  # Assuming your environment is defined here
import os
import tqdm

from LowAbstractionEnvironment import LockupGame

from Models import TwinLayerNN

# Initialize the environment
env = LockupEnvRay()
obs_space_shape = env.observation_space.shape[0]
action_space_size = env.action_space.n

# !!! it is highkey faster at this scale on my cpu, but i be using my cpu
device = torch.device('cuda')
# device = torch.device('cpu')

# Initialize the neural network, optimizer, and loss function
model = TwinLayerNN(input_size=obs_space_shape, output_size=action_space_size).to(device)
optimizer = optim.Adam(model.parameters(), lr=0.1)
# loss_fn = nn.CrossEntropyLoss()  # For discrete action spaces



# Training loop (basic interaction)
def train(env : LockupEnvRay, model : nn.Module, episodes=10, epochs=1):
  progress_bar = tqdm.tqdm(range(episodes * epochs), desc = 'Training Cycles', unit = 'Cyc')

  for loop in progress_bar:
    illegal_actions_this_epoch = 0
    legal_actions_this_epoch = 0

    obs_dict, _ = env.reset()
    done = False
    rewards = None

    sum_loss = 0
    sum_rounds = 0

    while not done:
      initial_scores = env.game.player_scores
      saved_forward_log_probs : list[None | torch.Tensor] = [None, None, None, None]

      losses = [torch.tensor([0], device=device)]


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
          # print("illegal logprob", log_prob)

          loss = -200 * log_prob
          losses.append(losses[-1] + loss)

          loss.backward(retain_graph = True)
          
          # print("CRSSH")

          indices = np.where(action_mask == 1)[0]

          randomized_action = np.random.choice(indices)
          action_dict = {player : randomized_action}
          
          illegal_actions_this_epoch += 1

        else:

          legal_actions_this_epoch += 1

        
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
          loss = -.25 * log_prob_tensor

          losses.append(losses[-1] + loss)

        else:
          loss = 1 * log_prob_tensor

          

          losses.append(loss + losses[-1])

        loss.backward(retain_graph=(player != 3))

      batch_loss = losses[-1]
      sum_loss += batch_loss
      sum_rounds += 1
      
      # print('\r', episode, env.game.player_scores, batch_loss if type(batch_loss) == int else batch_loss.item(), '                                   ', end = '')
      
      # batch_loss.backward()
      optimizer.step()

    progress_bar.set_postfix(loss=(sum_loss.item()/sum_rounds), illegal_actions_ratio=(illegal_actions_this_epoch/(illegal_actions_this_epoch + legal_actions_this_epoch)))

  
    if loop % episodes == (episodes - 1):
      torch.save(model, f'Checkpoints/Checkpoint-{loop // episodes}.pt')



def render_eval_round(env : LockupEnvRay, model : nn.Module):
  torch.set_grad_enabled(False)
  
  obs_dict, _ = env.reset()

  print("Random lead set to be: ", [i for i in obs_dict.keys()][0])

  done = False
  rewards = None

  while not done:

    for _ in range(4):
      # print(saved_forward_log_probs)
      # Prepare observations for the model
      player = [i for i in obs_dict.keys()][0]

      # Human player
      if (player == 0):
        print()
        print("YOUR TURN")
        print("Your hand:", env.game.str_player_hand(0))
        
        print("Leftside Player:", LockupGame.str_collection_info(env.game.played_cards_this_round[1]))
        print("Cross Player:", LockupGame.str_collection_info(env.game.played_cards_this_round[2]))
        print("Rightside Player", LockupGame.str_collection_info(env.game.played_cards_this_round[3]))
        print("Legal plays:", env.game.str_collection_info(env.game.present_action_space(0)))
        print("Legal play indices:", np.where(env.game.present_action_space(0) == 1)[0])

        while True:
          action_desired = int(input("Your play: "))

          if action_mask[action_desired] == 0:
            print(LockupGame._index_to_card_name(action_desired), "is not a legal play")
            continue

          if input("Confirm " + LockupGame._index_to_card_name(action_desired) + "(y/n): ").lower() == "y":
            break

        obs_dict, rewards, dones, infos, = env.step({0 : np.ndarray(action_desired)})
        print(f"Player {player} plays {LockupGame._index_to_card_name(action_desired)}")

        # Check if the episode has ended
        done = dones["__all__"]
        continue

      # print("Player:", player)
      obs_array = np.array(obs_dict[player])  # Convert dict to array of observations
      obs_tensor = torch.tensor(obs_array, dtype=torch.float, device=device)

      action_mask = env.game.present_action_space(player)

      action_logits = model.forward(obs_tensor) # ? .clone()
      actions = action_logits.flatten()  # Choose actions greedily
      action_dist = torch.distributions.Categorical(actions)
      action = action_dist.sample()

      if action_mask[action.detach().to(device='cpu').item()] == 0:
        
        # print("CRSSH")
        print(f"Bot {player} tried to take illegal action")
        indices = np.where(action_mask == 1)[0]
        action = np.random.choice(indices)
        action_dict = {player : action}

      else:
        print(f"Bot {player} plays {LockupGame._index_to_card_name(action.item())}")
        action_dict = {player : action.detach().to(device='cpu').numpy()}

      # Step through the environment
      obs_dict, rewards, dones, infos = env.step(action_dict)
      

      # Check if the episode has ended
      done = dones["__all__"]



  torch.set_grad_enabled(True)




# Run the training loop
if (os.path.isfile('TwinLayerNN.pt')):
  model = torch.load('TwinLayerNN.pt', weights_only=False).to(device)
train(env, model, episodes=100, epochs=10)
# render_eval_round(env, model)
torch.save(model, 'TwinLayerNN.pt')