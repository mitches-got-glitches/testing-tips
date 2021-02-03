from typing import Optional, Any, Tuple, Dict

import pytest
import pandas as pd

class Case:
    """Container for a test case, with optional test ID.

    Attributes
    ----------
        label : str
            Optional test ID. Will be displayed for each test when
            running `pytest -v`.
        kwargs: Parameters used for the test cases.

    Examples
    --------
    >>> Case(label="some test name", foo=10, bar="some value")
    >>> Case(foo=99, bar="some other value")   # no name given

    See Also
    --------
    source: https://github.com/ckp95/pytest-parametrize-cases

    """

    def __init__(self, label: Optional[str] = None, **kwargs):
        """Initialise objects."""
        self.label = label
        self.kwargs = kwargs
        # Makes kwargs accessible with dot notation.
        self.__dict__.update(kwargs)

    def __repr__(self) -> str:
        """Return string."""
        return f"Case({self.label!r}, **{self.kwargs!r})"


def create_dataframe(tuple_data):
    """Create pandas df from tuple data with a header."""
    return pd.DataFrame.from_records(tuple_data[1:], columns=tuple_data[0])


def get_case_parameters(request: pytest.FixtureRequest) -> Dict[str, Any]:
    """Return the parameters for each test case from the fixture reqest."""
    case = request.param
    return {k: get_fixture_value(request, v) for k, v in case.kwargs.items()}


def slice_dataframes(
    start_end: Tuple[int, int],
    *dfs: pd.DataFrame,
) -> Tuple[pd.DataFrame, ...]:
    """Slices each DataFrame by the given integer indexes."""
    # Make sure the end index given is actually in the DataFrames.
    for df in dfs:
        if start_end[1] not in df.index:
            raise IndexError(
                "Slice end is not in range of df.index: "
                f"{start_end[1]} > {len(df.index)-1}"
            )

    slice_ = slice(*start_end)
    return tuple([df.loc[slice_, :] for df in dfs])


def get_fixture_value(request: pytest.FixtureRequest, v: Any) -> Any:
    """Get the fixture value if it is a fixture, else v."""
    try:
        return request.getfixturevalue(v)
    except (pytest.FixtureLookupError, TypeError):
        return v


def parametrize_cases(*cases: Case):
    """More user friendly parameterize cases testing.

    Source: https://github.com/ckp95/pytest-parametrize-cases
    """
    for case in cases:
        if not isinstance(case, Case):
            raise TypeError(f"{case!r} is not an instance of Case")

    first_case = cases[0]
    first_args = first_case.kwargs.keys()
    argument_string = ",".join(sorted(first_args))

    case_list = []
    ids_list = []
    for case in cases:
        args = case.kwargs.keys()

        if args != first_args:
            raise ValueError(
                f"Inconsistent signature: {first_case!r}, {case!r}"
            )

        case_tuple = tuple(value for key, value in sorted(case.kwargs.items()))
        case_list.append(case_tuple)
        ids_list.append(case.label)

    if len(first_args) == 1:
        # otherwise it gets passed to the test function as a singleton tuple
        case_list = [i[0] for i in case_list]

    return pytest.mark.parametrize(
        argnames=argument_string, argvalues=case_list, ids=ids_list
    )
