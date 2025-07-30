import math

from cthulhu_src.services.cross_exchange_manager import get_free_transitions
from cthulhu_src.services.pair import Pair, Order


def test_get_free_transitions(tmp_path, monkeypatch):
    monkeypatch.setattr('cthulhu_src.services.cross_exchange_manager.AVAILABLE_IO_DIR', str(tmp_path))
    (tmp_path / 'ex1_output.txt').write_text('ex1_BTC\n')
    (tmp_path / 'ex2_input.txt').write_text('ex2_BTC\n')

    pairs = get_free_transitions(['ex1', 'ex2'])
    assert pairs == [Pair('ex1_BTC', 'ex2_BTC', [Order(1, math.inf)])]
