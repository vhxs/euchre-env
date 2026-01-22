import pytest

from game.cards import Card, Deck


def test_card_string_representation():
    card = Card(Deck.HEART, Deck.JACK)
    assert str(card) == "JH"


def test_make_trump_promotes_left_bower():
    deck = Deck()
    deck.make_trump(Deck.HEART)
    left_bower = deck.get_card(Deck.DIAMOND, Deck.JACK)
    assert left_bower.suit == Deck.HEART


def test_score_cards_prioritizes_bowers():
    deck = Deck()
    deck.make_trump(Deck.HEART)
    deck.score_cards(Deck.SPADE, Deck.HEART)

    right_bower = deck.get_card(Deck.HEART, Deck.JACK)
    left_bower = deck.get_card(Deck.DIAMOND, Deck.JACK)
    trump_ace = deck.get_card(Deck.HEART, Deck.ACE)
    lead_ace = deck.get_card(Deck.SPADE, Deck.ACE)

    assert deck.get_score(right_bower) > deck.get_score(left_bower)
    assert deck.get_score(left_bower) > deck.get_score(trump_ace)
    assert deck.get_score(trump_ace) > deck.get_score(lead_ace)


def test_get_score_requires_score_cards():
    deck = Deck()
    card = deck.get_card(Deck.CLUB, Deck.NINE)
    with pytest.raises(AttributeError):
        _ = deck.get_score(card)
