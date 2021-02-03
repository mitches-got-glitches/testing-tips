"""Parametrisation demonstration - slicing a DataFrame into separate tests."""
from typing import Callable, List, Optional
import warnings

import numpy as np
import pandas as pd
from pandas._typing import Level
from pandas._testing import assert_frame_equal
import pytest

from .helpers import (
    Case,
    create_dataframe,
    slice_dataframes,
)


def add_N2_markers(markers: pd.DataFrame) -> pd.DataFrame:
    """Add N2 markers after N markers to denote imputations.

    Implements these rules:

    * Add an N2 in the period directly following an N, except when there
      is an M, N or T marker already, and the period following is not
      covered by a new base period (i.e. < Jan+1).

    * Add an N2 in the next available (not M or T) period when an N is
      followed by an M or T marker, except when there is an N marker
      already, and the next available period is not covered by a new
      base period (i.e. < Jan+1).

    """
    N_markers_to_deal_with = (markers == 'N')

    MNT_exists = markers.isin(['M', 'N', 'T'])
    MT_exists = markers.isin(['M', 'T'])

    # Initialise the mask with all False.
    mask = pd.DataFrame().reindex_like(markers).fillna(False)

    while N_markers_to_deal_with.any(1).any():

        # Shift the mask forward excluding any Trues in Jan, since we
        # don't want to add N2 markers in a period covered by the next
        # base period (which is refreshed in Jan - applies Feb-Jan+1).
        after_N_markers = shift_mask(N_markers_to_deal_with, exclude=[1])

        # Create a new mask for N2's if there are no M, N or T markers
        # in the next period ahead and append to existing mask.
        new_mask = after_N_markers & ~MNT_exists
        mask = mask | new_mask

        # The N markers we still have to deal with are those that are
        # followed by an M or T, so set those and loop until all are
        # dealt with.
        N_markers_to_deal_with = after_N_markers & MT_exists

    return markers.mask(mask, 'N2')


class TestAddN2Codes:
    """A set of component tests for add_N2_codes."""

    @pytest.fixture
    def input_data(self):
        """Return the input data for testing add_N2_codes."""
        df = create_dataframe(
            [
                (   # columns
                    '01/01/2017', '01/02/2017', '01/03/2017', '01/04/2017', '01/05/2017', '01/06/2017',
                    '01/07/2017', '01/08/2017', '01/09/2017', '01/10/2017', '01/11/2017', '01/12/2017',
                    '01/01/2018', '01/02/2018', '01/03/2018',
                ),
                ('', '', '', 'N', '', '', '', 'N', 'T', '', '', '', '', '', ''),
                ('', 'N', 'N', '', '', '', '', 'N', 'N', '', 'M', '', '', 'N', ''),
                ('N', '', '', '', '', '', '', '', '', '', '', '', '', '', ''),
                ('', '', '', '', '', 'N', '', '', '', 'N', '', '', 'N', '', ''),
                ('', '', '', '', '', '', '', 'M', '', 'N', 'M', '', '', '', ''),
                ('', '', '', 'N', '', '', 'T', '', 'N', 'T', '', 'N', '', '', ''),
            ],
        )
        df.columns = pd.to_datetime(df.columns, dayfirst=True)
        return df

    @pytest.fixture
    def expout_data(self):
        """Return the expected output for testing add_N2_codes."""
        df = create_dataframe(
            [
                (   # columns
                    '01/01/2017', '01/02/2017', '01/03/2017', '01/04/2017', '01/05/2017', '01/06/2017',
                    '01/07/2017', '01/08/2017', '01/09/2017', '01/10/2017', '01/11/2017', '01/12/2017',
                    '01/01/2018', '01/02/2018', '01/03/2018',
                ),
                ('', '', '', 'N', 'N2', '', '', 'N', 'T', 'N2', '', '', '', '', ''),
                ('', 'N', 'N', 'N2', '', '', '', 'N', 'N', 'N2', 'M', '', '', 'N', 'N2'),
                ('N', '', '', '', '', '', '', '', '', '', '', '', '', '', ''),
                ('', '', '', '', '', 'N', 'N2', '', '', 'N', 'N2', '', 'N', '', ''),
                ('', '', '', '', '', '', '', 'M', '', 'N', 'M', 'N2', '', '', ''),
                ('', '', '', 'N', 'N2', '', 'T', '', 'N', 'T', 'N2', 'N', 'N2', '', ''),
            ],
        )
        df.columns = pd.to_datetime(df.columns, dayfirst=True)
        return df

    def test_adds_N2_after_N_when_not_in_Jan(
            self,
            input_data,
            expout_data,
    ):
        """Unit test 1 for basic case: add_N2_markers."""
        # GIVEN a DataFrame of strings with N, M and T markers
        # WITH some N's directly followed by an N, M or a T
        # WHEN add_N2_markers returns
        # THEN the resulting DataFrame has N2's the period after N
        # WHERE there is not already an N, M or T

        # Use first two rows for this test.
        this_test_input = input_data.loc[0:1, :]
        this_test_expout = expout_data.loc[0:1, :]

        true_output = add_N2_markers(this_test_input)

        assert_frame_equal(true_output, this_test_expout)

    def test_that_add_N2_markers_doesnt_add_N2_in_Jan(
            self,
            input_data,
            expout_data,
    ):
        """Unit test 2 for add_N2_markers."""
        # GIVEN a DataFrame of strings with N markers
        # WITH some N codes in January
        # WHEN add_N2_markers returns
        # THEN the resulting DataFrame has N2's the period after N
        # EXCEPT when the N code is in January

        # Use 3rd and 4th rows for this test.
        this_test_input = input_data.loc[2:3, :]
        this_test_expout = expout_data.loc[2:3, :]

        true_output = add_N2_markers(this_test_input)

        assert_frame_equal(true_output, this_test_expout)

    def test_that_adds_N2_markers_after_M_and_T(
        self,
        input_data,
        expout_data,
    ):
        """Unit test 2 for add_N2_markers."""
        # GIVEN a DataFrame of strings with N markers
        # WITH some T's and M's directly following an N
        # WHEN add_N2_markers returns
        # THEN the resulting DataFrame has N2's the period after M or T
        # WHERE there is not already an N, M or T

        # Use 5th and 6th row for this test.
        this_test_input = input_data.loc[4:5, :]
        this_test_expout = expout_data.loc[4:5, :]

        true_output = add_N2_markers(this_test_input)

        assert_frame_equal(true_output, this_test_expout)


def shift_mask(
    mask: pd.DataFrame,
    periods: int = 1,
    axis: int = 1,
    exclude: Optional[List[int]] = None,
    only_include: Optional[List[int]] = None,
) -> pd.DataFrame:
    """Shift a boolean mask by given number of periods.

    There are additional options to exclude or only include any months
    passed to these arguments as an iterable (using their integer
    equivalent). An argument should be passed to only one of these
    parameters on each function call.

    Parameters
    ----------
    mask: DataFrame
        The boolean mask to shift.
    periods: int, default 1
        The number of periods to shift by (currently only months).
    axis: {0, 1} int, default 1
        The axis to shift on {0:'index', 1:'columns'}.
    exclude: list of ints, optional
        The monthly periods to exclude from the shift.
    only_include: list of ints, optional
        The only monthly periods to include in the shift.

    Returns
    -------
    DataFrame
        The shifted boolean mask.
    """
    if exclude and only_include:
        warnings.warn(
            "Only one of either exclude or only_include should be passed. "
            "Using exclude.",
            UserWarning,
        )

    if exclude or only_include:
        months = axis_vals_as_frame(mask, axis=1, converter=lambda x: x.month)

        if exclude:
            mask = mask & (~months.isin(exclude))

        elif only_include:
            mask = mask & months.isin(only_include)

    return mask.shift(periods, axis=axis).fillna(False)


def axis_vals_as_frame(
    df: pd.DataFrame,
    axis: int = 0,
    levels: Optional[Level] = None,
    converter: Callable[[pd.Index], pd.Index] = None,
) -> pd.DataFrame:
    """Broadcast axis values across the DataFrame.

    Pick the axis and optional MultiIndex level. Optionally
    transform the index object before broadcasting.

    Parameters
    ----------
    df: DataFrame
    axis: {0, 1}, int default 0
        The axis values to broadcast: {0:'index', 1:'columns'}.
    levels: int or str
        Either the integer position or the name of the level.
    converter: callable
        A function to transform an index object.

    Returns
    -------
    DataFrame
        The broadcast axis values with optional transformation.
    """
    vals = {0: df.index, 1: df.columns}.get(axis)

    if levels:
        vals = vals.get_level_values(levels)

    if converter:
        vals = converter(vals)

    # Prepare the values to pass to np.tile which reshapes to the df.
    if not isinstance(vals, np.ndarray):
        vals = vals.values
    reps = (df.shape[axis ^ 1], 1)

    if axis == 0:
        # Reshape vals to a column and reverse reps if axis is 0.
        vals = vals[:, None]
        reps = reps[::-1]

    df_out = df.copy()
    df_out.loc[:, :] = np.tile(vals, reps)

    return df_out
