import random

class Suits:
    HEART, SPADE, DIAMOND, CLUB = range(4)
    suits_repr = {HEART: 'H', SPADE: 'S', DIAMOND: 'D', CLUB: 'C'}
    values_repr = ['9', '10', 'J', 'Q', 'K', 'A']
    suits_ids = {y: x for x, y in suits_repr.items()}
    values_ids = {val: i for i, val in enumerate(values_repr)}
    # 2 = 'J' is special

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        suits_repr = Suits.suits_repr[self.suit]
        values_repr = Suits.values_repr[self.value]
        return f"{values_repr}{suits_repr}"

    def __eq__(self, other):
        return (self.suit == other.suit) and (self.value == other.value)

class Player:
    def __init__(self, idx):
        self.idx = idx
        self.hand = []

    def deal(self, cards):
        self.hand.extend(cards)

    def remove_card(self, card):
        self.cards.remove(card)

    def print_hand(self):
        print("Hand: " + " ".join([str(card) for card in self.hand]))

    def swap_card(self, new_card):
        while True:
            old_card_str = input("Which to discard?: ")
            try:
                suit = Suits.suits_ids[old_card_str[-1]]
                value = Suits.values_ids[old_card_str[:-1]]
            except (IndexError, KeyError):
                print(f"Card {old_card_str} not in hand!")
                continue
            old_card = Card(suit, value)
            if old_card not in self.hand:
                print(f"Card {old_card_str} not in hand!")
            else:
                self.hand.remove(old_card)
                self.hand.append(new_card)
                self.print_hand()
                return
    
class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        self.cards.clear()
        for suit in range(4):
            for value in range(6):
                self.cards.append(Card(suit, value))
        # shuffle
        random.shuffle(self.cards)

    def deal(self, player):
        to_deal = []
        for _ in range(5):
            to_deal.append(self.cards.pop())
        player.deal(to_deal)

    def take_top(self):
        return self.cards.pop()

    def add(self, card):
        self.cards.append(card)

class Euchre:
    def __init__(self, stick_the_dealer=False):
        self.score1 = 0
        self.score2 = 0
        self.deck = Deck()
        self.dealer = random.randint(0, 4)
        self.stick_the_dealer = stick_the_dealer
        self.players = [Player(p) for p in range(4)]

        self.play()

    def play(self):
        while not self.finished():
            winner, score = self.play_round()
            if winner == "1":
                self.score1 += score
            else:
                self.score2 += score

            self.dealer = (self.dealer + 1) % 4

        self.announce_winner()

    def play_round(self):
        self.deck.reset()
        for player in self.players:
            self.deck.deal(player)

        return "1", 10

    def bidding_round_one(self):
        maybe_trump_card = self.deck.take_top()
        player_number = (self.dealer + 1) % 4
        for _ in range(4):
            self.players[player_number].print_hand()
            take_card = input(f"Top card: {str(maybe_trump_card)}. Pick up? (y/n) ")
            if take_card.lower() == 'y':
                self.players[player_number].swap_card(maybe_trump_card)
                return True
            player_number = (player_number + 1) % 4
        self.deck.append(maybe_trump_card)
        return False

    def bidding_round_two(self):
        pass
        
    def finished(self):
        if self.score1 >= 10 or self.score2 >= 10:
            return True
        return False

    def announce_winner(self):
        if self.score1 >= 10:
            print("Team 1 wins!")
        else:
            print("Team 2 wins!")

if __name__ == "__main__":
    game = Euchre()