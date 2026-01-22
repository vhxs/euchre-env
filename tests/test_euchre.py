from game.euchre import Euchre


def test_compute_winner_score_non_alone_partial_tricks():
    game = Euchre()
    assert game.compute_winner_score(3, alone=False) == 1


def test_compute_winner_score_all_tricks_with_partner():
    game = Euchre()
    assert game.compute_winner_score(5, alone=False) == 2


def test_compute_winner_score_all_tricks_alone():
    game = Euchre()
    assert game.compute_winner_score(5, alone=True) == 4
