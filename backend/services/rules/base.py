"""Abstract base class for all AML rules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from models.schemas import Alert


class AMLRule(ABC):
    """Every AML rule must implement rule_name, description, and evaluate."""

    @property
    @abstractmethod
    def rule_name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @abstractmethod
    def evaluate(self, transactions: pd.DataFrame, context: dict[str, Any]) -> list[Alert]:
        """Run the rule against the given transactions.

        Parameters
        ----------
        transactions : pd.DataFrame
            Customer transactions with columns matching TransactionRecord fields.
        context : dict
            Additional data such as ``watchlist_df`` and ``high_risk_countries_df``.

        Returns
        -------
        list[Alert]
        """
        ...
