import gymnasium as gym
from gymnasium import spaces
from .Round import Round
from .Player import Player

class LockdownEnv(gym.Env):
    def __init__(self):
        super().__init__()

        self.max_hand_size = 13

        self.max_score = 20
        self.dealer = 0
        self.round = Round()
        self.players = [Player(i) for i in range(4)]

        # Dynamic action space, initialized as a placeholder
        self.action_space = spaces.Discrete(1)  # Placeholder, will be set dynamically

        # Observation space: each card represented as (rank, suit)
        # Assuming a max hand size of 10 cards
        
        self.observation_space = spaces.Box(
            low=0, high=14, shape=(self.max_hand_size, 2), dtype=int
        )  # (rank, suit) for each card in hand

    def reset(self):
        super().reset(seed=1248)
        observation, info = None, None
        self.event = 'GameStart'
        self._event_GameStart()
        observation = self.event_data_for_client
        self.event = 'NewRound'
        self.event_data_for_server = {}
        return observation, info

    def step(self, action):
        observation, reward, terminated, truncated, info, done = None, None, None, None

        if self.event == 'NewRound':
            self._event_NewRound()

        elif self.event == 'ShowTrickEnd':
            self._event_ShowTrickEnd()

        elif self.event == 'PlayTrick':
            # Check if the action index is within the current player's hand size
            player_hand_size = len(self.players[self.round.current_lead].getHand())
            if action >= player_hand_size:
                # Penalize invalid action
                reward = -1
                terminated = True
            else:
                self._event_PlayTrick_Action({'data': {'action': {'card': action}}})

        elif self.event == 'RoundEnd':
            reward = self._event_RoundEnd()

        elif self.event == 'GameOver':
            self._event_GameOver()
            terminated = True

        elif self.event == None:
            observation = None
            done = True

        # Dynamically set action space based on current player's hand size
        current_player = self.players[(self.round.current_lead + self.event_data_for_server.get('shift', 0)) % 4]
        hand_size = len(current_player.getHand())
        self.action_space = spaces.Discrete(hand_size) if hand_size > 0 else spaces.Discrete(1)

        # Update observation to include current player’s hand with ranks and suits
        observation = self.event_data_for_client
        return observation, reward, terminated, truncated, info, done

    def _event_GameStart(self):
        self.event_data_for_server = {}
        self.event_data_for_client = {
            'event_name': self.event,
            'broadcast': True,
            'data': {'players': [{'playerName': str(i)} for i in range(4)]}
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
                'players': [{'playerName': str(i), 'score': p.score} for i, p in enumerate(self.players)]
            }
        }
        self.event = 'PlayTrick'
        self.event_data_for_server = {'shift': 0}

    def _event_PlayTrick(self):
        shift = self.event_data_for_server['shift']
        current_player = self.players[(self.round.current_lead + shift) % 4]

        # Set action space based on the current player's hand size
        hand_size = len(current_player.getHand())
        self.action_space = spaces.Discrete(hand_size) if hand_size > 0 else spaces.Discrete(1)

        # Represent each card as {'rank': rank, 'suit': suit}
        hand_representation = [{"rank": card.rank, "suit": card.suit} for card in current_player.getHand()]
        while len(hand_representation) < self.max_hand_size:
            hand_representation.append({"rank": 0, "suit": 0})  # Pad with empty cards if hand is smaller

        self.event_data_for_client = {
            'event_name': self.event,
            'broadcast': True,
            'data': {
                'playerName': current_player.name,
                'hand': hand_representation,
                'cards': self.round.trick.info()
            }
        }

    def _event_PlayTrick_Action(self, action_data):
        shift = self.event_data_for_server['shift']
        player_pos = (self.round.current_lead + shift) % 4
        current_player = self.players[player_pos]

        if self.round.locktimes[player_pos] > 0:
            current_player.hand.popRandomCard()
            self.event = 'ShowTrickAction'
            self._event_ShowTrickAction()
            return

        # Use action to select card by index
        card_index = action_data['data']['action']['card']
        selected_card = current_player.hand[card_index]
        if not current_player.hand.canPlayCard(selected_card):
            self.event = 'PlayTrick'
            self._event_PlayTrick()
            return

        current_player.play(selected_card)
        self.event_data_for_server['shift'] += 1
        self.event = 'ShowTrickAction'
        self._event_ShowTrickAction()

    def render(self):
        if self.render_mode is not None:
            raise NotImplementedError

    def close(self):
        pass
