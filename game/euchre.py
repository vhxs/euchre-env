import random

from game.cards import Deck
from game.player import Player


class Euchre:
    def __init__(self, stick_the_dealer=False):
        self.score1 = 0
        self.score2 = 0
        self.deck = Deck()
        self.dealer = random.randint(0, 3)
        self.stick_the_dealer = stick_the_dealer
        self.players = [Player(p, self.deck) for p in range(4)]

    def start(self):
        try:
            self.play_game()
        except KeyboardInterrupt:
            exit(0)

    def reset(self):
        for player in self.players:
            player.hand.clear()

    def throw_in(self):
        self.reset()
        self.deck.reset()

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

    def finished(self):
        if self.score1 >= 10 or self.score2 >= 10:
            return True
        return False

    def announce_winner(self):
        if self.score1 >= 10:
            print("Team 1 wins!")
        else:
            print("Team 2 wins!")