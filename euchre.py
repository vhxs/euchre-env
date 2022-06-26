import random

class Suits:
    HEART, SPADE, DIAMOND, CLUB = range(4)
    suits_repr = {HEART: 'H', SPADE: 'S', DIAMOND: 'D', CLUB: 'C'}
    values_repr = ['9', '10', 'J', 'Q', 'K', 'A']
    suits_ids = {y: x for x, y in suits_repr.items()}
    values_ids = {val: i for i, val in enumerate(values_repr)}

    suits_complement = {HEART: DIAMOND, DIAMOND: HEART, SPADE: CLUB, CLUB: SPADE}

    def order(lead_suit, trump_suit):
        # there are 24 cards in a euchre deck
        radix = 24
        coef = 1
        scores = {}

        # not trump, not lead suit
        for suit in [s for s in range(4) if s not in [lead_suit, trump_suit]]:
            for value in range(6):
                scores[Card(suit, value)] = 0

        # leading suit
        coef *= radix
        for value in range(6):
            scores[Card[lead_suit, value]] = coef + value

        # trump suit
        coef *= radix
        for value in range(6):
            scores[Card[trump_suit, value]] = coef + value

        # left bower
        

    def choose_winner(plays):
        pass

class Card:
    def __init__(self, suit, value):
        # "real" suit is only for printing/parsing
        self.real_suit = suit
        self.suit = suit
        self.value = value

    def __str__(self):
        suits_repr = Suits.suits_repr[self.real_suit]
        values_repr = Suits.values_repr[self.value]
        return f"{values_repr}{suits_repr}"

    def __eq__(self, other):
        return (self.suit == other.suit) and (self.value == other.value)

    def make_trump(self, trump_suit):
        # should only be called on a Jack
        if self.value != Suits.values_ids['J']:
            raise ValueError("Trying to make non-Jack a trump card!")
        
        self.suit = trump_suit

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

    def choose_card(self, prompt, lead_suit=None):
        while True:
            self.print_hand()
            card_str = input(prompt)

            # parse input
            try:
                suit = Suits.suits_ids[card_str[-1]]
                value = Suits.values_ids[card_str[:-1]]
            except (IndexError, KeyError):
                print(f"Invalid card {card_str}!")
                continue

            # valid card, but not in hand
            card = Card(suit, value)
            if card not in self.hand:
                print(f"Card {card_str} not in hand!")
                continue

            # doesn't match lead suit
            if lead_suit is not None and self.has_suit(lead_suit):
                print(f"Must follow suit!")
                continue

            break
        return card

    def swap_card(self, new_card):
        # first pick up new card
        self.hand.append(new_card)

        # then discard
        old_card = self.choose_card("Which to discard? ")
        self.hand.remove(old_card)
        self.print_hand()

    def suits_in_hand(self):
        return [card.suit for card in self.hand]

    def has_suit(self, suit):
        return suit in self.suits_in_hand()

    def play_card(self, lead_suit):
        # choose card and remove from hand
        card = self.choose_card("Which card to play? ", lead_suit)
        self.hand.remove(card)
        return card
    
class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        # populate deck
        self.cards.clear()
        for suit in range(4):
            for value in range(6):
                self.cards.append(Card(suit, value))
        # shuffle it
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
        self.dealer = random.randint(0, 3)
        self.stick_the_dealer = stick_the_dealer
        self.players = [Player(p) for p in range(4)]

        # exit gracefully
        try:
            self.play_game()
        except KeyboardInterrupt:
            exit(0)

    def play_game(self):
        while not self.finished():
            winner, score = self.play_round()
            if winner == 0:
                self.score1 += score
            else:
                self.score2 += score

            self.dealer = (self.dealer + 1) % 4
            self.play_round()

        self.announce_winner()

    def reset(self):
        for player in self.players:
            player.hand.clear()

    def play_round(self):
        # deal to everyone
        self.reset()
        self.deck.reset()
        for player in self.players:
            self.deck.deal(player)

        # pick a suit
        success, caller, alone, suit = self.bidding_round_one()
        if not success:
            success, caller, alone, suit = self.bidding_round_two(suit)
            if not success:
                # should not happen in stick the dealer
                assert not self.stick_the_dealer
                print("Throw it in!")
                self.throw_in()
                self.play_round()
        else:
            trump = suit
        
        # play 5 tricks
        tricks1 = 0
        tricks2 = 0
        leader = (self.dealer + 1) % 4

        # skip partner if alone
        if alone:
            skip_player = (caller + 2) % 4
            if leader == skip_player:
                leader = (leader + 1) % 4
        else:
            skip_player = None

        for _ in range(5):
            leader = self.play_trick(leader, trump, skip_player)
            if leader % 2 == 0:
                tricks1 += 1
            else:
                tricks2 += 1
        
        # determine scoring, based on caller, alone, outcome
        # TODO calculate score

        return 0, 10

    def compute_winner_score(self, did_call, tricks, alone):
        if did_call:
            if tricks == 5:
                if not alone:
                    # called it and got all tricks, with partner
                    return 2
                else:
                    # got all of them alone
                    return 4
            else:
                # didn't get them all, alone or otherwise
                return 1
        else:
            # this is a euchre
            return 2

    def play_trick(self, leader, trump, skip_player=None):
        suit = None
        plays = {}
        for i in range(4):
            # choose player
            player = (leader + i) % 4

            # if skipped player, skip
            if skip_player is not None and player == skip_player:
                continue

            # choose card to play, following suit
            card = self.players[player].choose_card("What to play? ", suit)

            # set suit and card order if first player
            if suit is None:
                suit = card.suit
                Suits.order(suit, trump)

            # add to the trick
            plays[player] = card

        return 0

    def bidding_round_one(self):
        maybe_trump_card = self.deck.take_top()
        player_number = (self.dealer + 1) % 4
        for _ in range(4):
            self.players[player_number].print_hand()
            take_card = input(f"Top card: {str(maybe_trump_card)}. Have dealer pick up? (y/a/n) ")
            if (choice := take_card.lower()) in ['y', 'a']:
                self.players[self.dealer].swap_card(maybe_trump_card)
                alone = (choice == 'a')
                return True, player_number, alone, maybe_trump_card.suit
            player_number = (player_number + 1) % 4
        self.deck.add(maybe_trump_card)
        return False, -1, False, maybe_trump_card.suit

    def choose_suit(self, player, forbidden_suit, force_choice):
        possible_suits = [suit for suit in player.suits_in_hand() if suit != forbidden_suit]
        # check edge case
        if not possible_suits and force_choice:
            print(f"Forced to choose {Suits.suits_repr[forbidden_suit]}.")
            alone_choice = input("Alone? (y/n): ")
            if alone_choice.lower() == 'y':
                alone = True
            else:
                alone = False
            return True, forbidden_suit, alone

        possible_suits_str = " ".join([Suits.suits_repr[suit] for suit in possible_suits])
        if not force_choice:
            prompt = f"Choose suit among {possible_suits_str} or pass (p): "
        else:
            prompt = f"Choose suit among {possible_suits_str}: "
        while True:
            choice_str = input(prompt)
            # pass (if allowed)
            if choice_str.lower() == 'p' and not force_choice:
                return False, -1, False
            # otherwise choose trump
            try:
                choice = Suits.suits_ids[choice_str]
            except (IndexError, KeyError):
                print(f"Invalid choice {choice_str}")
            if choice not in possible_suits:
                print(f"Invalid choice {choice_str}")
            else:
                # don't forget to ask whether alone or not
                alone_choice = input("Alone? (y/n): ")
                if alone_choice.lower() == 'y':
                    alone = True
                else:
                    alone = False
                return True, choice, alone

    def bidding_round_two(self, forbidden_suit):
        player_number = (self.dealer + 1) % 4
        for i in range(4):
            player = self.players[player_number]
            force_choice = (i == 3) and self.stick_the_dealer
            player.print_hand()
            yes, choice, alone = self.choose_suit(player, forbidden_suit, force_choice)
            if yes:
                return True, player_number, alone, choice
            player_number = (player_number + 1) % 4
        # this can't happen in stick the dealer
        return False, -1, False, -1
        
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