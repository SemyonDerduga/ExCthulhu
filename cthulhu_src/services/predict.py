from __future__ import annotations

"""Simple ML-based ranking of arbitrage paths."""

from typing import List, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from .processor import Path


def rank_paths_ml(paths: List[Path], start_amount: float) -> List[Tuple[float, Path]]:
    """Rank arbitrage ``paths`` using a logistic regression model.

    The model is trained on the fly using path length and profit ratio as
    features. The function returns a list of ``(score, path)`` tuples sorted
    by descending score.
    """

    if not paths:
        return []

    features = []
    labels = []
    for path in paths:
        profit_ratio = path[-1][1] / start_amount
        features.append([len(path), profit_ratio])
        labels.append(1 if profit_ratio > 1.0 else 0)

    X = np.array(features)
    y = np.array(labels)

    if len(paths) > 1 and len(set(labels)) > 1:
        model = LogisticRegression()
        model.fit(X, y)
        scores = model.predict_proba(X)[:, 1]
    else:
        # fallback to profit ratio if there is not enough data for training
        scores = X[:, 1]

    ranked = sorted(zip(scores, paths), key=lambda x: x[0], reverse=True)
    return ranked


def rank_paths_advanced(
    paths: List[Path], start_amount: float, currency_list: List[str]
) -> List[Tuple[float, Path]]:
    """Rank arbitrage ``paths`` using a random forest model with extra features."""

    if not paths:
        return []

    features: List[List[float]] = []
    labels: List[int] = []

    for path in paths:
        profit_ratio = path[-1][1] / start_amount

        exchanges = set()
        currencies = set()
        for step in path:
            name = currency_list[step[0]]
            if "_" in name:
                ex, cur = name.split("_", 1)
            else:
                ex, cur = "", name
            exchanges.add(ex)
            currencies.add(cur)

        start_ex = currency_list[path[0][0]].split("_", 1)[0]
        end_ex = currency_list[path[-1][0]].split("_", 1)[0]

        features.append(
            [
                len(path),
                profit_ratio,
                len(exchanges),
                len(currencies),
                1.0 if start_ex == end_ex else 0.0,
            ]
        )
        labels.append(1 if profit_ratio > 1.0 else 0)

    X = np.array(features)
    y = np.array(labels)

    if len(paths) > 1 and len(set(labels)) > 1:
        model = RandomForestClassifier(n_estimators=50)
        model.fit(X, y)
        scores = model.predict_proba(X)[:, 1]
    else:
        # fallback to profit ratio if there is not enough data for training
        scores = X[:, 1]

    ranked = sorted(zip(scores, paths), key=lambda x: x[0], reverse=True)
    return ranked
