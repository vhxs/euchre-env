import random


class Card:

    def __init__(self, suit, value):
        self.face_suit = suit
        self.suit = suit
        self.value = value

    def __str__(self):
        suits_repr = Deck.suits_repr[self.face_suit]
        values_repr = Deck.values_repr[self.value]
        return f"{values_repr}{suits_repr}"

    def __eq__(self, other):
        return (self.face_suit == other.face_suit) and (self.value == other.value)


class Player:
    def __init__(self, idx, deck):
        self.idx = idx
        self.deck = deck
        self.hand = []

    def deal(self, cards):
        self.hand.extend(cards)

    def remove_card(self, card):
        self.hand.remove(card)

    def print_hand(self):
        print("Hand: " + " ".join([str(card) for card in self.hand]))

    def choose_card(self, prompt, lead_suit=None):
        while True:
            print(f"Player {self.idx}")
            self.print_hand()
            card_str = input(prompt)

            # parse input
            try:
                suit = Deck.suits_ids[card_str[-1]]
                value = Deck.values_ids[card_str[:-1]]
            # garbage input
            except (IndexError, KeyError):
                print(f"{card_str} is not a card!")
                continue

            # valid card, but not in hand
            card = self.deck.get_card(suit, value)
            if card not in self.hand:
                print(f"Card {card_str} not in hand!")
                continue

            # doesn't match lead suit
            if lead_suit is not None and card.suit != lead_suit and self.has_suit(lead_suit):
                print(f"Must follow suit!")
                continue

            print()
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
    HEART, SPADE, DIAMOND, CLUB = SUITS = range(4)
    NINE, TEN, JACK, QUEEN, KING, ACE = VALUES = range(6)

    suits_repr = {HEART: 'H', SPADE: 'S', DIAMOND: 'D', CLUB: 'C'}
    values_repr = ['9', '10', 'J', 'Q', 'K', 'A']
    suits_ids = {y: x for x, y in suits_repr.items()}
    values_ids = {val: i for i, val in enumerate(values_repr)}

    suits_complement = {HEART: DIAMOND, DIAMOND: HEART, SPADE: CLUB, CLUB: SPADE}

    def __init__(self):
        # create card objects, shouldn't change over lifetime of program
        self.cards = {}
        for suit in Deck.SUITS:
            for value in Deck.VALUES:
                card = Card(suit, value)
                self.cards[(suit, value)] = card

        # populate deck
        self.reset()

    def reset(self):
        for card in self.cards.values():
            card.suit = card.face_suit
        self.deck = list(self.cards.values())
        random.shuffle(self.deck)

    def deal(self, player):
        to_deal = []
        for _ in range(5):
            card = self.take_top()
            to_deal.append(card)
        player.deal(to_deal)

    def get_card(self, face_suit, value):
        return self.cards[(face_suit, value)]

    def take_top(self):
        return self.deck.pop()

    def add(self, card):
        self.deck.append(card)

    def score_cards(self, lead_suit, trump_suit):
        self.score = {}
        for card in self.cards.values():
            if card.suit == lead_suit:
                score = 24 + card.value
            elif card.suit == trump_suit:
                # a bower
                if card.value == Deck.JACK:
                    # the right
                    if card.face_suit == trump_suit:
                        score = 24 * 24 * 24 * 24
                    # the left
                    else:
                        score = 24 * 24 * 24
                # not a bower
                else:
                    score = 24 * 24 + card.value
            # just a card
            else:
                score = -1
            self.score[(card.face_suit, card.value)] = score

    def get_score(self, card):
        face_suit = card.face_suit
        value = card.value

        return self.score[(face_suit, value)]

    def make_trump(self, trump):
        opposite_suit = Deck.suits_complement[trump]
        left = self.get_card(opposite_suit, Deck.JACK)
        left.suit = trump


class Euchre:
    def __init__(self, stick_the_dealer=False):
        self.score1 = 0
        self.score2 = 0
        self.deck = Deck()
        self.dealer = random.randint(0, 3)
        self.stick_the_dealer = stick_the_dealer
        self.players = [Player(p, self.deck) for p in range(4)]

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

    def throw_in(self):
        self.reset()
        self.deck.reset()

    def play_round(self):
        # deal to everyone
        self.reset()
        self.deck.reset()
        for player in self.players:
            self.deck.deal(player)

        # pick a suit and caller
        success, caller, alone, trump = self.bidding_round_one()
        if not success:
            success, caller, alone, trump = self.bidding_round_two(trump)
            if not success:
                # should not happen in stick the dealer
                assert not self.stick_the_dealer
                print("Throw it in!")
                self.throw_in()
                self.play_round()

        # change suit of the left
        self.deck.make_trump(trump)

        # track only caller's tricks
        tricks = 0
        leader = (self.dealer + 1) % 4

        # skip partner if alone
        if alone:
            skip_player = (caller + 2) % 4
            if leader == skip_player:
                leader = (leader + 1) % 4
        else:
            skip_player = None

        # play 5 tricks, keep track of caller's tricks
        for _ in range(5):
            leader = self.play_trick(leader, trump, skip_player)
            if leader % 2 == caller % 2:
                tricks += 1

        # not a euchre
        if tricks >= 3:
            winner = caller % 2
            score = self.compute_winner_score(tricks, alone)
        # euchred
        else:
            winner = (caller + 1) % 2
            score = 2

        return winner, score

    def compute_winner_score(self, tricks, alone):
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
            card = self.players[player].play_card(suit)

            # set suit and card order if first player
            if suit is None:
                suit = card.suit
                self.deck.score_cards(suit, trump)

            # add to the trick
            plays[player] = card

        sorted_plays = sorted([(self.deck.get_score(card), player) for player, card in plays.items()], reverse=True)
        new_leader = sorted_plays[0][1]

        print("Trick over")

        return new_leader

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
        possible_suits = set([suit for suit in player.suits_in_hand() if suit != forbidden_suit])
        # check edge case
        if not possible_suits and force_choice:
            print(f"Forced to choose {Deck.suits_repr[forbidden_suit]}.")
            alone_choice = input("Alone? (y/n): ")
            if alone_choice.lower() == 'y':
                alone = True
            else:
                alone = False
            return True, forbidden_suit, alone

        possible_suits_str = " ".join([Deck.suits_repr[suit] for suit in possible_suits])
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
                choice = Deck.suits_ids[choice_str]
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
