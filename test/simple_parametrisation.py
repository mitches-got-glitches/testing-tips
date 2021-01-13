"""Simple parametrisation example"""
from precon import round_and_adjust
from pandas.testing import assert_frame_equal, assert_series_equal

import pytest

from .helpers import create_dataframe


@pytest.fixture
def round_and_adjust_input():
    """Return the input_data data for testing round and adjust."""
    df = create_dataframe(
        [
            ('Regions', 'Expenditure 1', 'Expenditure 2', 'Expenditure 3', 'Expenditure 4'),
            ('Region 1', 9.224971796646614, 7.983121359330053, 7.963320362205599, 8.602730488285397),
            ('Region 2', 14.581712261164467, 14.247897819508536, 14.977573354216672, 15.663123390301266),
            ('Region 3', 13.932903666079595, 22.367047854514798, 15.291098991449905, 15.351572230061103),
            ('Region 4', 17.961964526687407, 17.42795380770113, 18.08031852172324, 16.861532785772862),
            ('Region 5', 20.59213475943632, 20.108083253903878, 22.31727689778805, 19.03074505486427),
            ('Region 6', 23.706312989985605, 17.865895905041608, 21.370411872616533, 24.490296050715088),
        ],
    )
    return df.set_index('Regions')


@pytest.mark.parametrize("decimals", [0, 2, 5, 8])
def test_round_and_adjust_with_decimals(
        round_and_adjust_input,
        decimals,
):
    """Test for round_and_adjust with various decimal arguments."""
    # GIVEN the input data and varying decimals argument
    # WHEN round_and_adjust returns
    # THEN the output sum is equal to the unrounded values sum
    # AND the output is rounded to the correct decimal places
    rounded_values = round_and_adjust(round_and_adjust_input, decimals=decimals)

    assert_series_equal(rounded_values.sum(), round_and_adjust_input.sum())
    assert_frame_equal(
        rounded_values,
        rounded_values.round(decimals),
        # Define the require tolerance for the decimals.
        rtol=10**-(decimals+1)
    )


@pytest.mark.parametrize("axis", [1, 'columns'])
def test_round_and_adjust_works_on_column_axis(
        round_and_adjust_input,
        axis,
):
    """Test round_and_adjust axis argument with transposed input."""
    # GIVEN the transposed input data, decimals=2 and axis='columns'
    # WHEN round_and_adjust returns
    # THEN the output sum is equal to the unrounded values sum
    # AND the output is rounded to the correct decimal places
    round_and_adjust_input = round_and_adjust_input.T

    rounded_values = round_and_adjust(round_and_adjust_input, 2, axis)

    assert_series_equal(
        rounded_values.sum(axis),
        round_and_adjust_input.sum(axis),
    )
    assert_frame_equal(rounded_values, rounded_values.round(2))