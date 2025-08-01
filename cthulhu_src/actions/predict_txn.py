import logging
from collections import defaultdict

from cthulhu_src.services.exchange_manager import ExchangeManager
from cthulhu_src.services.processor import find_paths
from cthulhu_src.services.arbitrage import find_paths_bellman_ford
from cthulhu_src.services.exchanges.batching_exchange import BatchingExchange
from cthulhu_src.services.cross_exchange_manager import get_free_transitions
from cthulhu_src.services.predict import rank_paths_ml

"""ML-based ranking of arbitrage chains."""


async def run(
    ctx,
    max_depth: int,
    exchange_list: list,
    start_node: str,
    start_amount: float,
    cache_dir: str,
    current_node: str | None = None,
    current_amount: float | None = None,
    cached: bool = False,
    algorithm: str = "dfs",
    processes: int | None = None,
    prune_ratio: float = 0.0,
    batch_size: int = 20,
    proxy: tuple | list = (),
):
    """Run search and rank resulting chains using ML."""
    log = logging.getLogger("excthulhu")
    log.info(
        f'🤖 Predicting transactions with max depth {max_depth} for exchanges: {", ".join(exchange_list)}'
    )

    log.info("⬇️ Start loading data...")

    BatchingExchange.max_batch_size = batch_size
    exchange_manager = ExchangeManager(
        exchange_list, proxy, cached=cached, cache_dir=cache_dir
    )
    try:
        pairs = await exchange_manager.fetch_prices()
    finally:
        await exchange_manager.close()

    pairs += get_free_transitions(exchange_list)

    log.info("✅ Finish loading")

    log.info("⚙️ Start prepare data...")

    adj_dict = defaultdict(list)
    for pair in pairs:
        adj_dict[pair.currency_from].append(pair)

    currency_list = list(adj_dict.keys())

    adj_list = [
        {
            currency_list.index(pair.currency_to): pair.trade_book
            for pair in adj_dict[currency_from]
        }
        for currency_from in currency_list
    ]

    current_node_id = None
    if current_node:
        if current_node not in currency_list:
            log.error(
                f"❌ Current node {current_node} is not available in fetched data."
            )
            return
        current_node_id = currency_list.index(current_node)

    log.info("✅ Finish prepare data")

    if start_node not in currency_list:
        log.error(f"❌ Start node {start_node} is not available in fetched data.")
        return

    log.info("🔄 Start data processing...")
    if algorithm == "bellman-ford":
        paths = find_paths_bellman_ford(
            adj_list=adj_list,
            start_node=currency_list.index(start_node),
            start_amount=start_amount,
        )
    else:
        paths = find_paths(
            adj_list=adj_list,
            start_node=currency_list.index(start_node),
            start_amount=start_amount,
            current_node=current_node_id,
            current_amount=current_amount,
            max_depth=max_depth,
            prune_ratio=prune_ratio,
            num_workers=processes,
        )
    log.info("✅ Finish data processing")

    ranked = rank_paths_ml(paths, start_amount)

    result = [
        (score, [(currency_list[node[0]], node[1]) for node in path])
        for score, path in ranked
    ]

    for score, path in result:
        print(
            f"score={score:.3f}",
            *[f"{node[0]} ({node[1]})" for node in path],
            sep=" -> ",
            end="",
        )
        print(f" = {(path[-1][1] / start_amount - 1) * 100}%")

    log.info(f"🏆 Total count of ranked cycles:{len(result)}")
