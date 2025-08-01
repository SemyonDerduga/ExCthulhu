from cthulhu_src.services.predict import rank_paths_ml, rank_paths_advanced


def test_rank_paths_ml_ordering():
    start_amount = 1.0
    path_good = [(0, 1.0), (1, 2.0), (0, 1.5)]
    path_bad = [(0, 1.0), (1, 0.5), (0, 0.25)]

    ranked = rank_paths_ml([path_bad, path_good], start_amount)

    assert ranked[0][1] == path_good
    assert len(ranked) == 2


def test_rank_paths_advanced_ordering():
    start_amount = 1.0
    path_good = [(0, 1.0), (1, 2.0), (0, 1.5)]
    path_bad = [(0, 1.0), (1, 0.5), (0, 0.25)]
    currency_list = ["ex1_BTC", "ex1_USDT"]

    ranked = rank_paths_advanced([path_bad, path_good], start_amount, currency_list)

    assert ranked[0][1] == path_good
    assert len(ranked) == 2
