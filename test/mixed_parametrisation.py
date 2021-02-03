from typing import Sequence

import pandas as pd
from pandas._typing import Label
from pandas._testing import assert_frame_equal
import pytest

from .helpers import (
    Case,
    create_dataframe,
    get_case_parameters,
)


def get_base_price_imputations(
    to_impute: pd.DataFrame,
    group_on: Sequence[Label],
) -> pd.DataFrame:
    """Return the index labels where base price imputation occurs.

    A base price imputation is needed whenever any of the prices
    need to be imputed for a given period.
    """
    return (
        to_impute.groupby(group_on)
        .any()
        # The above groupby doesn't retain the column name, so rename.
        .rename_axis(to_impute.columns.name, axis=1)
        .pipe(subset_truthy)
        .assign(imputation_type='base_price')
    )


def subset_truthy(bool_mask: pd.DataFrame) -> pd.DataFrame:
    """Return the index labels where the bool mask is True as frame."""
    levels = list(range(bool_mask.columns.nlevels))
    return (
        bool_mask.stack(levels)
        .pipe(lambda x: x[x])
        .index.to_frame(index=False)
    )


@pytest.fixture
def imputations_input_data():
    """Return input data for imputations tests."""
    df = create_dataframe(
        [   # level_1 and level_2 cols are set to the index
            ('level_1', 'level_2', '2017-01-01', '2017-02-01', '2017-03-01', '2017-04-01'),
            ('A', 'foo', False, True, True, False),
            ('A', 'bar', False, False, True, False),
            ('A', 'baz', False, False, True, False),
            ('B', 'foo', False, False, False, False),
            ('B', 'bar', False, False, False, False),
            ('B', 'baz', False, False, False, False),
            ('C', 'foo', False, False, True, False),
            ('C', 'bar', False, False, True, True),
            ('C', 'baz', False, False, False, True),
            ('D', 'foo', False, False, False, False),
            ('D', 'bar', False, False, True, False),
            ('D', 'baz', False, False, False, True),
        ],
    )
    df = df.set_index(['level_1', 'level_2'])
    df.columns.name = 'quote_date'
    df.columns = pd.to_datetime(df.columns)

    return df


class TestGetBasePriceImputations:
    """Tests for the get_base_price_imputations function.

    Tests the following cases:

    * Grouping on the first level of a MultiIndex
    * Grouping on both levels of a MultiIndex

    """

    @pytest.fixture
    def expout_grouping_on_level_1(self):
        """Return exp output when grouping on level 1."""
        df = create_dataframe(
            [
                ('level_1', 'quote_date', 'imputation_type'),
                ('A', '2017-02-01', 'base_price'),
                ('A', '2017-03-01', 'base_price'),
                ('C', '2017-03-01', 'base_price'),
                ('C', '2017-04-01', 'base_price'),
                ('D', '2017-03-01', 'base_price'),
                ('D', '2017-04-01', 'base_price'),
            ],
        )
        df.quote_date = pd.to_datetime(df.quote_date)
        return df

    @pytest.fixture
    def expout_grouping_on_both_levels(self):
        """Return exp output when grouping on both levels."""
        df = create_dataframe(
            [
                ('level_1', 'level_2', 'quote_date', 'imputation_type'),
                ('A', 'bar', '2017-03-01', 'base_price'),
                ('A', 'baz', '2017-03-01', 'base_price'),
                ('A', 'foo', '2017-02-01', 'base_price'),
                ('A', 'foo', '2017-03-01', 'base_price'),
                ('C', 'bar', '2017-03-01', 'base_price'),
                ('C', 'bar', '2017-04-01', 'base_price'),
                ('C', 'baz', '2017-04-01', 'base_price'),
                ('C', 'foo', '2017-03-01', 'base_price'),
                ('D', 'bar', '2017-03-01', 'base_price'),
                ('D', 'baz', '2017-04-01', 'base_price'),
            ],
        )
        df.quote_date = pd.to_datetime(df.quote_date)
        return df

    @pytest.fixture(
        params=[
            Case(
                label="grouping_on_level_1",
                # GIVEN a boolean DataFrame with levels in MultiIndex on rows axis, time periods in column axis
                # AND a single level to group_on
                # WHEN the function returns
                # THEN the DataFrame is reduced to the level / time period indices
                # WHERE there is at least one True in the slice given by those indices
                # AND a new column 'imputation_type' is created with the value 'base_price'
                group_on="level_1",
                expout="expout_grouping_on_level_1",
            ),
            Case(
                label="grouping_on_both_levels",
                # Similar to above, just using both levels.
                group_on=['level_1', 'level_2'],
                expout="expout_grouping_on_both_levels",
            ),
        ],
        ids=lambda x: x.label,
    )
    def case_parameters(self, request):
        """Return the parameters for each test given by params."""
        return get_case_parameters(request)

    def test_cases(self, imputations_input_data, case_parameters):
        """Test both cases for get_base_price_imputations."""
        expected_output = case_parameters.pop('expout')

        output = get_base_price_imputations(
            imputations_input_data,
            **case_parameters,
        )

        assert_frame_equal(output, expected_output)