""" """
import pandas as pd
from pandas._testing import assert_frame_equal
import pytest

from .helpers import (
    Case,
    create_dataframe,
    get_case_parameters,
)

from src.kwargs_quality_adjustment import get_quality_adjustments

class TestGetQualityAdjustments:
    """Tests for get_quality_adjustments function."""

    @pytest.fixture
    def input_quality_values(self):
        """Return the quality_value input data for get_quality_adjustments.

        The important feature of this dataset is that it spans multiple
        years, as the function fills within the year.
        """
        df = create_dataframe([
            (   # columns
                '01/01/2017', '01/02/2017', '01/03/2017', '01/04/2017', '01/05/2017', '01/06/2017',
                '01/07/2017', '01/08/2017', '01/09/2017', '01/10/2017', '01/11/2017', '01/12/2017',
                '01/01/2018', '01/02/2018', '01/03/2018',
            ),
            (30, 30, 30, 32, 32, 32, 32, 32, 37, 37, 37, 37, 35, 30, 30),
            (500, 500, 480, 480, 480, 480, 480, 480, 450, 450, 450, 450, 400, 400, 400),
            (10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2),
            (10, 11, 11, 11, 11, 11, 12, 12, 12, 12, 14, 14, 13, 13, 13),
        ])
        df.columns = pd.to_datetime(df.columns, dayfirst=True)
        return df

    @pytest.fixture
    def expout_all_size_changes_true(self):
        """Return the expected output data for when no to_adjust or to_reset are passed."""
        df = create_dataframe([
            (   # columns
                '01/01/2017', '01/02/2017', '01/03/2017', '01/04/2017', '01/05/2017', '01/06/2017',
                '01/07/2017', '01/08/2017', '01/09/2017', '01/10/2017', '01/11/2017', '01/12/2017',
                '01/01/2018', '01/02/2018', '01/03/2018',
            ),
            (
                1, 1, 1, 1.0666667, 1.0666667, 1.0666667, 1.0666667, 1.0666667,
                1.233333, 1.233333, 1.233333, 1.233333, 1.1666667, 0.857142857, 0.857142857
            ),
            (1, 1, 0.96, 0.96, 0.96, 0.96, 0.96, 0.96, 0.9, 0.9, 0.9, 0.9, 0.8, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1),
            (1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.2, 1.4, 1.4, 1.3, 1, 1),
        ])
        df.columns = pd.to_datetime(df.columns, dayfirst=True)
        return df.astype('float64')

    @pytest.fixture
    def to_adjust_only_selected_size_changes_true(self):
        """Return the to_adjust boolean mask input data for get_quality_adjustments.

        This bool mask is only True for certain size changes. This
        mimics the W codes mask, as not all size changes are marked
        with a W code.
        """
        df = create_dataframe([
            (
                '01/01/2017', '01/02/2017', '01/03/2017', '01/04/2017', '01/05/2017', '01/06/2017',
                '01/07/2017', '01/08/2017', '01/09/2017', '01/10/2017', '01/11/2017', '01/12/2017',
                '01/01/2018', '01/02/2018', '01/03/2018',
            ),
            (False, False, False, True, False, False, False, False, False, False, False, False, False, True, False),
            (False, False, False, False, False, False, False, False, True, False, False, False, False, False, False),
            (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
            (False, False, False, False, False, False, False, False, False, False, False, True, False, False, False),
            (False, True, False, False, False, False, True, False, False, False, True, False, True, False, False),
        ])
        df.columns = pd.to_datetime(df.columns, dayfirst=True)
        return df

    @pytest.fixture
    def expout_only_selected_size_changes_true(self):
        """Return the expected output data for when only selected size
        changes are true, given by to_adjust.
        """
        df = create_dataframe([
            (
                '01/01/2017', '01/02/2017', '01/03/2017', '01/04/2017', '01/05/2017', '01/06/2017',
                '01/07/2017', '01/08/2017', '01/09/2017', '01/10/2017', '01/11/2017', '01/12/2017',
                '01/01/2018', '01/02/2018', '01/03/2018',
            ),
            (
                1, 1, 1, 1.0666667, 1.0666667, 1.0666667, 1.0666667, 1.0666667,
                1.0666667, 1.0666667, 1.0666667, 1.0666667, 1.0666667, 0.857142857, 0.857142857
            ),
            (1, 1, 1, 1, 1, 1, 1, 1, 0.9375, 0.9375, 0.9375, 0.9375, 0.9375, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1),
            (1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.2, 1.4, 1.4, 1.3, 1, 1),
        ])
        df.columns = pd.to_datetime(df.columns, dayfirst=True)
        return df.astype('float64')

    @pytest.fixture
    def to_reset(self):
        """Return the to_reset bool mask input data."""
        df = create_dataframe([
            (
                '01/01/2017', '01/02/2017', '01/03/2017', '01/04/2017', '01/05/2017', '01/06/2017',
                '01/07/2017', '01/08/2017', '01/09/2017', '01/10/2017', '01/11/2017', '01/12/2017',
                '01/01/2018', '01/02/2018', '01/03/2018',
            ),
            (False, False, False, False, False, False, False, False, False, False, True, False, False, False, False),
            (False, False, False, False, False, False, False, False, False, True, False, False, False, False, False),
            (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
            (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
            (False, False, False, True, False, False, False, False, False, False, False, False, False, False, False),
        ])
        df.columns = pd.to_datetime(df.columns, dayfirst=True)
        return df

    @pytest.fixture
    def expout_all_size_changes_true_with_imputations(self):
        """Return the expected output data for when all size changes are true
        and a set of imputations are passed.
        """
        df = create_dataframe([
            (   # columns
                '01/01/2017', '01/02/2017', '01/03/2017', '01/04/2017', '01/05/2017', '01/06/2017',
                '01/07/2017', '01/08/2017', '01/09/2017', '01/10/2017', '01/11/2017', '01/12/2017',
                '01/01/2018', '01/02/2018', '01/03/2018',
            ),
            (
                1, 1, 1, 1.0666667, 1.0666667, 1.0666667, 1.0666667, 1.0666667,
                1.233333, 1.233333, 1, 1, 0.945945946, 0.857142857, 0.857142857
            ),
            (1, 1, 0.96, 0.96, 0.96, 0.96, 0.96, 0.96, 0.9, 1, 1, 1, 0.888888889, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1),
            (
                1, 1.1, 1.1, 1, 1, 1, 1.0909091, 1.0909091, 1.0909091, 1.0909091,
                1.2727273, 1.2727273, 1.1818182, 1, 1,
            ),
        ])
        df.columns = pd.to_datetime(df.columns, dayfirst=True)
        return df.astype('float64')

    @pytest.fixture
    def expout_only_selected_size_changes_true_with_imputations(self):
        """Return the expected output data for when only selected size changes
        are true and a set of imputations are passed.
        """
        df = create_dataframe([
            (   # columns
                '01/01/2017', '01/02/2017', '01/03/2017', '01/04/2017', '01/05/2017', '01/06/2017',
                '01/07/2017', '01/08/2017', '01/09/2017', '01/10/2017', '01/11/2017', '01/12/2017',
                '01/01/2018', '01/02/2018', '01/03/2018',
            ),
            (
                1, 1, 1, 1.0666667, 1.0666667, 1.0666667, 1.0666667, 1.0666667,
                1.0666667, 1.0666667, 1, 1, 1, 0.857142857, 0.857142857
            ),
            (1, 1, 1, 1, 1, 1, 1, 1, 0.9375, 1, 1, 1, 1, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1),
            (
                1, 1.1, 1.1, 1, 1, 1, 1.0909091, 1.0909091, 1.0909091, 1.0909091,
                1.2727273, 1.2727273, 1.1818182, 1, 1,
            ),
        ])
        df.columns = pd.to_datetime(df.columns, dayfirst=True)
        return df.astype('float64')

    @pytest.fixture(
        params=[
            Case(
                label="just_sizes",
                quality_value="input_quality_values",
                expout="expout_all_size_changes_true",
            ),
            Case(
                label="sizes_with_to_adjust",
                quality_value="input_quality_values",
                to_adjust="to_adjust_only_selected_size_changes_true",
                expout="expout_only_selected_size_changes_true",
            ),
            Case(
                label="sizes_with_to_reset",
                quality_value="input_quality_values",
                to_reset="to_reset",
                expout="expout_all_size_changes_true_with_imputations",
            ),
            Case(
                label="size_with_to_adjust_and_to_reset",
                quality_value="input_quality_values",
                to_reset="to_reset",
                to_adjust="to_adjust_only_selected_size_changes_true",
                expout="expout_only_selected_size_changes_true_with_imputations",
            ),

        ],
        ids=lambda x: x.label,
    )
    def input_expout_combinator(self, request):
        """Return the fixtures for each test given by params."""
        # Dataclasses have an internal __dict__ attribute.
        return {
            k: request.getfixturevalue(v)
            for k, v in request.param.kwargs.items()
            # Default None will cause an error when getting fixture.
        }

    def test_selected_size_changes(
        self,
        input_expout_combinator,
    ):
        """Unit tests for get_quality_adjustments."""
        expected_output = input_expout_combinator.pop('expout')

        output = get_quality_adjustments(**input_expout_combinator)

        assert_frame_equal(output, expected_output)
