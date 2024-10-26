from .Round import Round
from .Player import Player

import gymnasium as gym


class LockdownEnv(gym.Env):
  def __init__ (self):

    self.max_score = 20
    self.dealer = 0
    self.round = Round()

    self.players = [Player(i) for i in range(0, 4)]

    self.action_space = gym.spaces.Discrete(1)
    self.observation_space = gym.spaces.Box(
      low=(0, 0, 0, 0), high=()
    )

    self.max_hand_size = 13


  def render(self):

    if self.render_mode != None:
      return NotImplementedError
    

  def close(self):
    # Functionally unnecessary, implemented to note that
    pass
  def reset(self):
    super().reset(seed=1248)

    observation, info = None, None

    self.event = 'GameStart'
    self._event_GameStart()
    observation = self.event_data_for_client
    self.event = 'NewRound'
    self.event_data_for_server = {}

    return observation, info



  def step(self, action_data):
    observation, reward, terminated, truncated, info, done = None, None, None, None

    if self.event == 'NewRound':
      self._event_NewRound()

    elif self.event == 'ShowTrickEnd':
      self._event_ShowTrickEnd()

    elif self.event == 'PlayTrick': # Could choose to implement version showing trick action
      action_data
      
      self._event_PlayTrick()
    
    elif self.event == 'RoundEnd':
      reward = self._event_RoundEnd()
    
    elif self.event == 'GameOver':
      self._event_GameOver()
      terminted = True
    
    elif self.event == None:
      observation = None
      done = True

    current_player = self.players[(self.round.current_lead + self.event_data_for_server.get('shift', 0)) % 4]
    hand_size = len(current_player.hand.info())
    self.action_space = gym.spaces.Discrete(hand_size) if hand_size > 0 else gym.spaces.Discrete(1)

    observation = self.event_data_for_client

    return observation, reward, terminated, truncated, info, done

  def _event_GameStart(self):
    self.event_data_for_server = {}
    self.event_data_for_client = {
      'event_name': self.event,
      'broadcast': True,
      'data': {
        'players':[
          {'playerName': '0'},
          {'playerName': '1'},
          {'playerName': '2'},
          {'playerName': '3'}
        ]
      }
    }

    for p in self.players:
      p.score = 0
    

    self.renderInfo = {'printFlag': False, 'Msg': ""}

  def _event_NewRound(self):
    self.round.reset()

    self.event_data_for_client = {
      'event_name': self.event,
      'broadcast': True,
      'data': {
        'players':[
          {'playerName': '0', 'score':self.players[0].score},
          {'playerName': '1', 'score':self.players[1].score},
          {'playerName': '2', 'score':self.players[2].score},
          {'playerName': '3', 'score':self.players[3].score}
        ]
      }
    }

    self.event = 'PlayTrick'
    self.event_data_for_server = {'shift':0}

  def _event_PlayTrick(self):

    shift = self.event_data_for_server['shift']
    current_player : Player = self.players[(self.round.current_lead + shift) % 4]

    hand_size = len(current_player.hand)
    self.action_space = gym.spaces.Discrete(hand_size)

    self.event_data_for_client = {
      'event_name': self.event,
      'broadcast': True,
      'data': {
        'playerName': current_player.name,
        'hand': str(current_player.hand.info()), # TODO: convert into dict {rank, suit} and pad out observerd hand with empty cards
        'cards': self.round.trick.info()
      }
    }

  def _event_PlayTrick_Action(self, action_data):
    shift = self.event_data_for_server['shift']

    player_pos = (self.round.current_lead + shift) % 4
    current_player = self.players[player_pos]

    if (self.round.locktimes[player_pos] > 0):
      current_player.hand.popRandomCard()
      self.event = 'ShowTrickAction'
      self._event_ShowTrickAction()
      return
    
    add_card_index = action_data['data']['action']['card']
    selected_card = current_player.hand[add_card_index]

    if not(current_player.hand.canPlayCard(selected_card)):
      self.event = 'PlayTrick'
      self._event_PlayTrick()
      return
    
    current_player.play(selected_card)
    self.event_data_for_server['shift'] += 1
    self.event = 'ShowTrickAction'
    self._event_ShowTrickAction()

  def _event_ShowTrickAction(self):

    self.event_data_for_client = {
      'event_name': self.event,
      'broadcast': True,
      'data': {
        'currentTrick' : self.round.trick.info()
      }
    }

    if (self.round.trick.winner is None):
      # Thus the trick hasn't ended
      self.event = 'PlayTrick'
    else:
      self.event = 'ShowTrickEnd'

  def _event_ShowTrickEnd(self):

    self.round.endTrick()

    self.event_data_for_client = {
      'event_name': self.event,
      'broadcast': True,
      'data': {
        'trickWinner': self.round.trick.winner,
        'winnerLockdown': self.round.trick.winner_lockdown, 
        'cards' : self.round.trick.info()
      }
    }

    if self.round.roundComplete:
      self.event = 'RoundEnd'
      self.event_data_for_server = {}
    else:
      self.event = 'PlayTrick'
      self.event_data_for_server = {'shift': 0}

  def _event_RoundEnd(self):

    for idx, val in enumerate(self.round.tricksWon):
      self.players[idx] += val

    
    self.event_data_for_client = {
      'event_name': self.event,
      'broadcast': True,
      'data': {
        'players':[
          {'playerName': '0', 'score':self.players[0].score},
          {'playerName': '1', 'score':self.players[1].score},
          {'playerName': '2', 'score':self.players[2].score},
          {'playerName': '3', 'score':self.players[3].score}
        ]
      }
    }

    best_score = max(self.players, key=lambda x:x.score)
    if best_score >= self.max_score:
      self.event = 'GameOver'
    else:
      self.event = 'NewRound'
    self.event_data_for_server = {}

    reward = {}
    for idx, player in enumerate(self.players):
      reward[player.name] = self.round.tricksWon[idx]

      if self.event == 'GameOver' and player.score == best_score:
        reward[player.name] += 5

    return reward

  def _event_GameOver(self):

    winner = max(self.players, key=lambda x:x.score)

    self.event_data_for_client = {
      'event_name': self.event,
      'broadcast': True,
      'data': {
        'players':[
          {'playerName': '0', 'score':self.players[0].score},
          {'playerName': '1', 'score':self.players[1].score},
          {'playerName': '2', 'score':self.players[2].score},
          {'playerName': '3', 'score':self.players[3].score}
        ], 
        'Winner' : winner.name
      }
    }








