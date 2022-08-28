from game.cards import Deck


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
