import torch
import tqdm
import numpy as np


import numpy as np
from LowAbstractionEnvironment import LockupGame
import FormalEnvironment

def test_lockup_game():
    game = LockupGame()
    
    # Test initial state
    assert game.dealer >= 0 and game.dealer < 4
    assert np.sum(game.held_cards) == 52
    assert np.sum(game.player_scores) == 0
    assert np.sum(game.player_lockup_timers) == 0
    
    # Test a few rounds of play
    for _ in range(20):
        player = game.next_player
        print("\nplayer", player)
        game.print_player_hand(player)
        action_space = game.present_action_space(player)
        game.print_player_hand(player)
        valid_actions = np.where(action_space == 1)[0]
        if len(valid_actions) > 0:
            action = np.random.choice(valid_actions)
            print("taken", LockupGame._index_to_card_name(action))
            next_player = game.make_play_and_state_next_player(player, action)
            # print("np", next_player)
            assert 0 <= next_player < 4 or next_player == -1
    
    print("Basic LockupGame test passed!")

test_lockup_game()
