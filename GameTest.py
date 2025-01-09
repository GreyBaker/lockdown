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
    for _ in range(330):
        player = game.next_player
        print("\nplayer", player)
        print(game.str_player_hand(player))
        action_space = game.present_action_space(player)
        str(LockupGame.str_collection_info(action_space))
        valid_actions = np.where(action_space == 1)[0]
        if len(valid_actions) > 0:
            action = np.random.choice(valid_actions)
            print("taken", LockupGame._index_to_card_name(action))
            next_player = game.make_play_and_state_next_player(player, action)
            # print("np", next_player)
            assert 0 <= next_player < 4 or next_player == -1
        if next_player == -1:
            if any([score >= 20 for score in game.player_scores]):
                break
            next_player = game._deal_round_and_state_first_player(True)
    
    print(game.player_scores)
    print("Basic LockupGame test passed!")

test_lockup_game()
