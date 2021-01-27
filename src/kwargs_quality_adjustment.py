"""Handles creation af adjustment factors for quality adjustment."""
from typing import Optional, Callable

import pandas as pd


def get_quality_adjustments(
    quality_value: pd.DataFrame,
    to_reset: Optional[pd.DataFrame] = None,
    to_adjust: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Return cumulative quality adjustment factors for given values.

    Accumulates the quality adjustments across each Feb-Jan+1 window,
    resetting back to no adjustment (a factor of 1) if a reset occurs.
    By default, adjustment factors are determined by dividing quality
    values by the value in the period before, but this can be subset
    using `to_adjust`_.

    Parameters
    ----------
    quality_value : DataFrame
        The quality value used to calculate quality adjustments.
    to_reset : DataFrame
        Boolean mask of quality adjustments to be reset.
    to_adjust : DataFrame
        Boolean mask of values to be adjusted.

    Returns
    -------
    DataFrame
        Cumulative adjustment factors for base prices.

    """
    # Divide size by the period before.
    adjustment_factors = quality_value.div(quality_value.shift(1, axis=1))

    if to_adjust is not None:
        adjustment_factors[~to_adjust] = 1

    if to_reset is not None:
        # Get the inverse cumulative growth for resetting.
        impute_resets = get_cumulative_adjustments(adjustment_factors).pow(-1)
        adjustment_factors = adjustment_factors.mask(to_reset, impute_resets)

    # Fill data lost in first period with 1 i.e. no adjustment.
    return get_cumulative_adjustments(adjustment_factors).fillna(1)


def get_cumulative_adjustments(
    adjustment_factors: pd.DataFrame
) -> pd.DataFrame:
    """Get cumprod of adjustment factors for the Feb-Jan+1 window."""
    return adjustment_factors.pipe(
        shifted_within_year_apply,
        lambda x: x.cumprod(axis=1),
        axis=1,
    )


def shifted_within_year_apply(
    df: pd.DataFrame,
    method: Callable[[pd.DataFrame], pd.DataFrame],
    axis: int = 0,
) -> pd.DataFrame:
    """Apply the given method within year for Feb - Jan+1 timespan."""
    return (
        df
        .shift(-1, axis=axis)
        .groupby(lambda x: x.year, axis=axis)
        .apply(method)
        .shift(1, axis=axis)
    )