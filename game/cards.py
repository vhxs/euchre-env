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
