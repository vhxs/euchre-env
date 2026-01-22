from game.cards import Deck
from game.player import Player


def test_player_deal_and_has_suit():
    deck = Deck()
    player = Player(0, deck)
    cards = [
        deck.get_card(Deck.HEART, Deck.NINE),
        deck.get_card(Deck.SPADE, Deck.ACE),
    ]
    player.deal(cards)

    assert player.has_suit(Deck.HEART) is True
    assert player.has_suit(Deck.DIAMOND) is False


def test_player_remove_card():
    deck = Deck()
    player = Player(0, deck)
    card = deck.get_card(Deck.CLUB, Deck.TEN)
    player.deal([card])

    player.remove_card(card)
    assert card not in player.hand
