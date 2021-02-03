from typing import Mapping, Sequence

import pandas as pd
from pandas._testing import assert_frame_equal
import pytest

from .helpers import (
    Case,
    create_dataframe,
    parametrize_cases,
)

def filter_retailer_items(
    df: pd.DataFrame,
    alt_data_filter: Mapping[int, Sequence[int]],
) -> pd.DataFrame:
    """Filter items from retailers present in alt sources data.

    Drops rows containing shop codes and their items that are covered in the
    alternative sources pipeline to prevent double counting.

    Parameters
    ----------
    df: DataFrame
    alt_data_filter: dictionary key=retailer codes: value=list of item codes
        The shop/item codes covered in the alternative data sources
        pipeline, used for dropping rows that match.

    Returns
    -------
    DataFrame
        Local collection data after filtering out Alt source data.

    """
    for shop_code, items in alt_data_filter.items():
        df = df.query('not (item_id == @items and shop_code == @shop_code)')

    return df


class TestFilterRetailerItems:
    """Tests for filtering out retailer/items present in AS data from LC data.

    Filter cases tested:
    * 1 retailer/1 item
    * 1 retailer/2 item
    * 1 retailer/all item
    * 2 retailer/some item
    * 1 retailer/0 item
    * 0 retailer/0 item
    """

    @pytest.fixture
    def filter_retailer_input(self):
        """Create input dataframe for filter_retailer_items function."""
        return create_dataframe(
            [
                ('shop_code', 'item_id'),
                (12, 987),
                (12, 987),
                (12, 654),
                (12, 321),
                (34, 987),
                (34, 765),
                (56, 876),
                (56, 543),
            ],
        )

    @parametrize_cases(
        Case(
            label="1_retailer_1_item",
            alt_data_filter={12: [654]},
            expout=create_dataframe([
                ('shop_code', 'item_id'),
                (12, 987),
                (12, 987),
                (12, 321),
                (34, 987),
                (34, 765),
                (56, 876),
                (56, 543),
            ]),
        ),
        Case(
            label="1_retailer_2_item",
            alt_data_filter={12: [654, 321]},
            expout=create_dataframe([
                ('shop_code', 'item_id'),
                (12, 987),
                (12, 987),
                (34, 987),
                (34, 765),
                (56, 876),
                (56, 543),
            ]),
        ),
        Case(
            label="1_retailer_all_item",
            alt_data_filter={12: [987, 654, 321]},
            expout=create_dataframe([
                ('shop_code', 'item_id'),
                (34, 987),
                (34, 765),
                (56, 876),
                (56, 543),
            ]),
        ),
        Case(
            label="2_retailer_some_item",
            alt_data_filter={
                12: [654, 321],
                34: [987],
            },
            expout=create_dataframe([
                ('shop_code', 'item_id'),
                (12, 987),
                (12, 987),
                (34, 765),
                (56, 876),
                (56, 543),
            ]),
        ),
        Case(
            label="1_retailer_0_item",
            alt_data_filter={12: []},
            expout=create_dataframe([
                ('shop_code', 'item_id'),
                (12, 987),
                (12, 987),
                (12, 654),
                (12, 321),
                (34, 987),
                (34, 765),
                (56, 876),
                (56, 543),
            ]),
        ),
        Case(
            label="0_retailer_0_item",
            alt_data_filter={},
            expout=create_dataframe([
                ('shop_code', 'item_id'),
                (12, 987),
                (12, 987),
                (12, 654),
                (12, 321),
                (34, 987),
                (34, 765),
                (56, 876),
                (56, 543),
            ]),
        ),
    )
    def test_cases(
        self,
        filter_retailer_input,
        alt_data_filter,
        expout,
    ):
        """Test the different filtering cases."""
        output_df = filter_retailer_items(filter_retailer_input, alt_data_filter)
        assert_frame_equal(output_df.reset_index(drop=True), expout)