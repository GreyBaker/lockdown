from .Hand import Hand

class Player:
    def __init__(self, id):
        self.name = str(id)
        self.hand = Hand()
        self.score = 0
        # self.cards_seen = [False for _ in range(52)] 

    def play(self, card):
        return self.hand.playCard(card)
    
    def getHand(self):
        pass # TODO

    def hasSuit(self, suit_id : int):
        return len(self.hand.hand[suit_id]) > 0
