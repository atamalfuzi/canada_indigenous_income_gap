"""Reading the fixed-width files and putting each year on one set of codes. No downloads."""
import numpy as np
import pandas as pd
import pytest

import data


def raw_frame(year, **changes):
    """One record per row of each coded variable, set to a harmless value unless changed."""
    n = max((len(v) for v in changes.values()), default=1)
    base = {"ABOID": 6, "AGEGRP": 12, "BFNMEMB": 1 if year == 2006 else 0, "CITIZEN": 1, "CMA": 535, "ETHDER": 5, "FPTWK": 1,
            "HDGREE": 9, "HHSIZE": 2, "KOL": 1, "MARSTH": 2, "REGIND": 1 if year == 2006 else 0, "TOTINC": 50000, "WAGES": 40000,
            "WKSWRK": 52 if year == 2006 else 6, "WEIGHT": 37.0}
    base |= {"GENDER": 1, "COVID_ERB": 99_999_999} if year == 2021 else {"SEX": 1}
    if year == 2006:
        base["MARST"] = 2
    base |= {f"WT{i + 1}": 0.0 for i in range(data.REPLICATES[year][0])}
    return pd.DataFrame({k: changes.get(k, [v] * n) for k, v in base.items()})


def test_read_fixed_slices_columns_by_position():
    frame = data.read_fixed(b"12 3.5\r\n45 7.5\r\n", {"A": (1, 2), "B": (4, 3)})
    assert frame.A.tolist() == [12, 45]
    assert frame.B.tolist() == [3.5, 7.5]


def test_read_fixed_refuses_uneven_records():
    with pytest.raises(ValueError):
        data.read_fixed(b"123\r\n45\r\n", {"A": (1, 2)})


@pytest.mark.parametrize("year", [2006, 2011, 2016])
def test_layouts_do_not_overlap(year):
    spans = sorted(data.LAYOUTS[year].values())
    assert all(a[0] + a[1] <= b[0] for a, b in zip(spans, spans[1:]))


@pytest.mark.parametrize("year", [2006, 2011, 2016])
def test_layouts_have_every_replicate_weight(year):
    assert sum(k.startswith("WT") for k in data.LAYOUTS[year]) == data.REPLICATES[year][0]


def test_registered_and_band_codes_differ_in_2006():
    yes = data.harmonise(raw_frame(2006, REGIND=[2], BFNMEMB=[2]), 2006)
    assert yes.registered.all() and yes.band.all() and yes.registered_band.all()
    for year in (2011, 2016, 2021):
        d = data.harmonise(raw_frame(year, REGIND=[1], BFNMEMB=[0]), year)
        assert d.registered.all() and not d.band.any() and d.registered_no_band.all()


def test_more_than_one_identity_sets_each_indicator_unless_registered():
    d = data.harmonise(raw_frame(2016, ABOID=[4]), 2016)
    assert d.first_nations.all() and d.metis.all() and d.inuit.all() and d.indigenous.all()
    d = data.harmonise(raw_frame(2016, ABOID=[4], REGIND=[1]), 2016)
    assert not (d.first_nations.any() or d.metis.any() or d.inuit.any())


def test_marital_status_merges_married_and_common_law_after_2006():
    d = data.harmonise(raw_frame(2011, MARSTH=[1, 2, 3, 4, 5, 6]), 2011)
    assert d.marital.tolist() == ["never", "couple", "couple", "separated", "divorced", "widowed"]
    d = data.harmonise(raw_frame(2006, MARSTH=[1, 2, 3, 4, 5]), 2006)
    assert d.marital.tolist() == ["divorced", "couple", "separated", "never", "widowed"]


def test_2021_uses_gender_and_other_years_use_sex():
    assert data.harmonise(raw_frame(2021, GENDER=[1, 2]), 2021).female.tolist() == [True, False]
    assert data.harmonise(raw_frame(2016, SEX=[1, 2]), 2016).female.tolist() == [True, False]


def test_area_keeps_large_areas_and_groups_the_rest():
    assert data.area(pd.Series([535, 421, 999, 988])).tolist() == [535, 30, 999, 30]  # Quebec City is in the group, as in A1b


def test_income_missing_codes_become_missing():
    d = data.harmonise(raw_frame(2016, TOTINC=[1000, 88_888_888, 99_999_999]), 2016)
    assert d.totinc.isna().tolist() == [False, True, True]
    d = data.harmonise(raw_frame(2006, TOTINC=[1000, 8_888_888, 9_999_999]), 2006)
    assert d.totinc.isna().tolist() == [False, True, True]


def test_ancestry_codes_follow_each_years_list():
    assert data.harmonise(raw_frame(2006, ETHDER=[3, 47, 1]), 2006).ancestry_only.tolist() == [True, True, False]
    assert data.harmonise(raw_frame(2021, ETHDER=[1, 3]), 2021).ancestry_only.tolist() == [True, False]
    assert not data.harmonise(raw_frame(2021, ETHDER=[1], ABOID=[2]), 2021).ancestry_only.any()


def test_covid_benefit_code_reads_as_none_and_not_available_stays_missing():
    d = data.harmonise(raw_frame(2021, COVID_ERB=[5000, 99_999_999, 88_888_888]), 2021)
    assert d.covid_erb.iloc[:2].tolist() == [5000, 0]
    assert np.isnan(d.covid_erb.iloc[2])


def test_sample_applies_the_a1b_conditions():
    d = data.harmonise(raw_frame(2016, CITIZEN=[1, 2, 1, 1, 1, 1], AGEGRP=[9, 9, 8, 17, 16, 16], KOL=[1, 1, 1, 1, 4, 3],
                                 HDGREE=[1, 1, 1, 1, 1, 88], HHSIZE=[7, 7, 7, 7, 7, 8]), 2016)
    assert data.sample(d).index.tolist() == [0]
