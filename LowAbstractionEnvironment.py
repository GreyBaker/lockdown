import numpy as np



class LockupGame:
  suits = {0:'C', 1:'S', 2:'D', 3:'H'}

  def __init__(self):
    self.dealer = -1
    self.trick_winner = -1
    self._deal_round_and_state_first_player()
    self._clean_scores()

  def _clean_scores(self):
    self.player_scores = np.zeros((4,), dtype=np.int32) # Only in one-round variant


  def _deal_round_and_state_first_player(self, force_random_dealer : bool = False) -> int:
    # Cleaning

    # Reset scores and timers
    self.player_lockup_timers = np.zeros((4,), dtype=np.int32)
    
    # Reset dealing and turn order information
    self.dealer = np.random.randint(0, 3+1) if (self.dealer == -1 or force_random_dealer) else (self.dealer + 1) % 4
    self.next_player = self.dealer
    self.lead_player = self.dealer

    # Reset card existance
    self.played_cards_this_round = np.zeros((4, 53), dtype=np.int32)
    self.discarded_cards = np.zeros((4, 52), dtype=np.int32)
    self.held_cards = np.zeros((4, 52), dtype=np.int32)

    # Deal out cards
    deck = [i for i in range(52)]
    np.random.shuffle(deck)

    for player in range(4):
      for card_idx in range(13):
        card = deck.pop(0)

        self.held_cards[player, card] = 1

    return self.next_player


  def present_observation_space(self, player_id : int) -> np.ndarray:
    # A given agent always 'feels' like they're player 0

    # self.player_lockup_timers = np.zeros((4,), dtype=np.int32)
    plt = np.roll(self.player_lockup_timers, -player_id)
    
    # self.player_scores = np.zeros((4,), dtype=np.int32)
    ps = np.roll(self.player_scores, -player_id)

    # self.lead_player = np.zeros((4,), dtype=np.int32) # Helps identify passing cards
    lp = np.zeros((4, ), dtype=np.int32)
    lp[self.lead_player] = 1
    lp = np.roll(lp, -player_id)

    # self.played_cards_this_round = np.zeros((4, 53), dtype=np.int32)
    pctr = np.roll(self.played_cards_this_round, -player_id).flatten()

    # self.discarded_cards = np.zeros((4, 52), dtype=np.int32)
    dc = np.roll(self.discarded_cards, -player_id).flatten()

    # self.held_cards = np.zeros((4, 52), dtype=np.int32)
    hc = self.held_cards[player_id]

    # self.unknown_cards = np.zeros((1, 52))
    uc = self.held_cards.copy()
    uc = np.delete(uc, player_id, axis = 0)
    uc = uc.sum(axis=0)
    
    # Could later choose to track actions across time or otherwise develop a profile
    # print("BASIC SHAPES")
    # print(plt.shape, ps.shape, lp.shape, pctr.shape, dc.shape, hc.shape, uc.shape)
    obs = np.concat((plt, ps, lp, pctr, dc, hc, uc))
    # 4 in 0-4, 4 in 0-32, 4 in 0-1, 212 in 0-1, 208 in 0-1, 52 in 0-1, 52 in 0-1

    return obs
    

  def present_action_space(self, player_id : int) -> np.ndarray:
    """Returns a mask of valid actions
    choosing lockup cards IS handled here"""

    acts = np.zeros((53,), dtype=np.int32)

    # Player is in lockup case
    if self.player_lockup_timers[player_id] > 0:
      acts[52] = 1
      return acts
    
    lead = -1
    for i in range(3):
      player_to_check = (self.lead_player + i) % 4

      if self.played_cards_this_round[player_to_check].sum() < 1:
        break
      elif self.played_cards_this_round[player_to_check, 52] > 0:
        continue

      for j in range(4):
        if np.sum(self.played_cards_this_round[player_to_check, 13*j:13*(j+1)], axis=0) > 0: # ??? Could do this as a reshape and sum
          lead = j
          break
      if lead != -1:
        break

    # Player leads case
    if lead == -1:
      # Nonclubs available case
      if sum(self.held_cards[player_id, 13:]) > 0:
        for card in range(13, 52):
          acts[13:52] = self.held_cards[player_id, 13:52]
      # Only clubs available case
      else:
        acts[0:52] = self.held_cards[player_id]

      return acts

    # Follow cases
    # Has on suit
    if sum(self.held_cards[player_id, 13*lead:13*(lead+1)]) > 0:
      acts[13*lead:13*(lead+1)] = self.held_cards[player_id, 13*lead:13*(lead+1)]

    # Off suit
    else:
      acts[0:52] = self.held_cards[player_id]


    # Face clubs
    combined_play = self.played_cards_this_round[:, 13:52].sum(axis=0).reshape(3, 13).sum(axis=0)
    for i in [9, 10, 11]:
      if combined_play[i] > 0 and self.held_cards[player_id, i] > 0:
        acts[i] = 1


    return acts

  def make_play_and_state_next_player(self, player_id : int, action_id : int) -> int:
    # For now, just assumes it's a valid action
    assert 0 <= action_id < 53


    # Modify
    if action_id == 52:
      indices = np.where(self.held_cards[player_id] == 1)[0]

      selected_card = np.random.choice(indices)

      self.held_cards[player_id, selected_card] = 0
      self.discarded_cards[player_id, selected_card] = 1
      self.played_cards_this_round[player_id, 52] = 1

      self.player_lockup_timers[player_id] -= 1

    else:
      # This can be factored out easily, but this is more verbose
      self.held_cards[player_id, action_id] = 0
      self.played_cards_this_round[player_id, action_id] = 1


    # Upkeep
    # Continue case
    if self.played_cards_this_round.sum(axis=1).sum(axis=0) < 4:
      self.next_player = (self.next_player + 1) % 4
      return self.next_player
    # Clean case
    else:
      return self._cycle_trick_and_state_first_player()
  

  def _cycle_trick_and_state_first_player(self) -> int:
    # Evaluate trick

    lead_suit = -1
    best_player = self.lead_player
    best_rank = -1
    clubs_observed = 0
    for i in range(4):
      current_player = (self.lead_player + i) % 4

      card_played = np.where(self.played_cards_this_round[current_player] == 1)[0]
      if card_played == 52:
        continue

      suit_id, card_rank = divmod(card_played, 13)

      if lead_suit == -1:
        lead_suit = suit_id

      if suit_id == 0:
        clubs_observed += 1

      if lead_suit == suit_id and card_rank >= best_rank:
        best_player = current_player
        best_rank = card_rank

    self.trick_winner = best_player
    self.player_scores[best_player] += 1
    self.player_lockup_timers[best_player] += clubs_observed

    # Upkeep
    if self.held_cards.sum(axis=1).sum(axis=0) == 0:
      return -1 # Signals that the round is over. Demands a new deal
    
    for i in range(4):
      self.discarded_cards[i] += self.played_cards_this_round[i, :52]
    self.played_cards_this_round = np.zeros((4, 53), dtype=np.int32)

    self.lead_player = best_player
    assert 0 <= self.lead_player < 4
    self.next_player = best_player
    return self.lead_player


  @staticmethod
  def _index_to_card_name(card_index : int) -> str:
    assert 0 <= card_index < 53

    if card_index == 52:
      return "Emp"

    suit_id, card_id = divmod(card_index, 13)
    card_id += 2

    return f"{LockupGame.suits[suit_id]}{card_id:02}"
  
  @staticmethod
  def str_collection_info(collection) -> str:
    assert len(collection) <= 53

    return ("".join([LockupGame._index_to_card_name(idx) + ", " if collection[idx] == 1 else "" for idx in range(len(collection))]))

  
  def str_player_hand(self, player_id : int) -> str:

    return LockupGame.str_collection_info(self.held_cards[player_id])



