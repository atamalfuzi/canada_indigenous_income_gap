"""Get the Statistics Canada individuals public use microdata files and put four years on one set of codes."""
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
RAW = ROOT / "data"
OUTPUT, FIGURES = ROOT / "output", ROOT / "figures"
BASE = "https://www150.statcan.gc.ca/n1/pub/98m0001x/2023001/"

YEARS = (2006, 2011, 2016, 2021)
# Census or survey year: the zip, and the data file inside it.
FILES = {2006: ("cen06_ind_95m0028x_part_rec06.zip", "Individual file/indiv_pumf06.dat"),
         2011: ("nhs11_ind_99m0001x_part_enm11.zip", "Individual file/data_donnees.dat"),
         2016: ("cen16_ind_98m0001x_part_rec16.zip", "2016 Census Individuals PUMF 98M0001X Recensement 2016 FMGD des particuliers/data_donnees_2016_ind.dat"),
         2021: ("cen21_ind_98m0001x_part_rec21.zip", "data_donnees_2021_ind_v2.csv")}
INCOME_YEAR = {2006: 2005, 2011: 2010, 2016: 2015, 2021: 2020}
# Random groups and the divisor each user guide gives for their squared deviations (section on sampling variability).
REPLICATES = {2006: (8, 56), 2011: (8, 56), 2016: (16, 240), 2021: (16, 35)}


def wts(year, start, width):
    return {f"WT{i + 1}": (start + i * width, width) for i in range(REPLICATES[year][0])}


# First column and width, from the layout files in each zip. 2021 is a CSV.
LAYOUTS = {
    2006: {"ABOID": (1, 1), "AGEGRP": (2, 2), "BFNMEMB": (7, 1), "CITIZEN": (25, 1), "CMA": (28, 3), "ETHDER": (61, 2),
           "FPTWK": (64, 1), "HDGREE": (84, 2), "HHSIZE": (91, 1), "KOL": (118, 1), "MARST": (132, 1), "MARSTH": (133, 1),
           "REGIND": (204, 1), "SEX": (222, 1), "TOTINC": (226, 7), "WAGES": (254, 7), "WEIGHT": (261, 11),
           "WKSWRK": (272, 2), **wts(2006, 276, 11)},
    2011: {"ABOID": (1, 1), "AGEGRP": (2, 2), "BFNMEMB": (8, 1), "CITIZEN": (36, 1), "CMA": (39, 3), "ETHDER": (74, 2),
           "FPTWK": (77, 1), "HDGREE": (93, 2), "HHSIZE": (101, 1), "KOL": (123, 1), "MARSTH": (142, 1),
           "REGIND": (211, 1), "SEX": (229, 1), "TOTINC": (234, 7), "WAGES": (256, 7), "WEIGHT": (263, 18),
           "WKSWRK": (281, 1), **wts(2011, 284, 18)},
    2016: {"WEIGHT": (7, 16), **wts(2016, 23, 16), "ABOID": (279, 1), "AGEGRP": (280, 2), "BFNMEMB": (286, 1),
           "CITIZEN": (321, 1), "CMA": (324, 3), "ETHDER": (367, 2), "FPTWK": (370, 1), "HDGREE": (391, 2),
           "HHSIZE": (399, 1), "KOL": (427, 1), "MARSTH": (445, 1), "REGIND": (510, 1), "SEX": (530, 1),
           "TOTINC": (539, 8), "WAGES": (565, 8), "WKSWRK": (573, 1)},
}
COLUMNS_2021 = ["ABOID", "AGEGRP", "BFNMEMB", "CITIZEN", "CMA", "COVID_ERB", "ETHDER", "FPTWK", "GENDER", "HDGREE", "HHSIZE",
                "KOL", "MARSTH", "REGIND", "TOTINC", "WAGES", "WEIGHT", "WKSWRK", *wts(2021, 0, 0)]

# The census metropolitan areas A1b kept as their own categories. The other named areas form one group, as does 999.
LARGE_CMA = {205, 462, 505, 535, 537, 602, 799, 825, 835, 933, 935}
NOT_CMA = 999
# ETHDER codes for Indigenous origins with no other origin reported. The list of origins differs every year.
INDIGENOUS_ORIGINS = {2006: {3, 47}, 2011: {1}, 2016: {1}, 2021: {1}}
NOT_AVAILABLE = 8_888_888  # anything at or above this in an income field is a missing code


def download(years=YEARS):
    RAW.mkdir(exist_ok=True)
    for year in years:
        name = FILES[year][0]
        request = urllib.request.Request(BASE + name, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=900) as r:
            (RAW / name).write_bytes(r.read())


def read_fixed(raw, layout):
    """Slice fixed-width bytes into float columns, which is many times faster than pandas.read_fwf on these files."""
    length = raw.index(b"\n") + 1
    if len(raw) % length:
        raise ValueError("records are not all the same length")
    rows = np.frombuffer(raw, dtype="S1").reshape(-1, length)
    return pd.DataFrame({name: pd.to_numeric(rows[:, start - 1:start - 1 + width].view(f"S{width}").ravel().astype(str),
                                             errors="coerce")
                         for name, (start, width) in layout.items()})


def read_year(year, root=RAW):
    """The columns this project uses, as Statistics Canada codes them."""
    name, member = FILES[year]
    with zipfile.ZipFile(root / name) as z, z.open(member) as f:
        if year == 2021:
            frame = pd.read_csv(f, usecols=lambda c: c.upper() in COLUMNS_2021)
            return frame.rename(columns=str.upper)
        return read_fixed(f.read(), LAYOUTS[year])


def harmonise(raw, year):
    """One set of names and codes for every year."""
    late = year > 2006
    d = pd.DataFrame({"year": year, "aboid": raw.ABOID, "agegrp": raw.AGEGRP, "citizen": raw.CITIZEN, "kol": raw.KOL,
                      "hdgree": raw.HDGREE, "hhsize": raw.HHSIZE, "cma": raw.CMA, "ethder": raw.ETHDER,
                      "fptwk": raw.FPTWK, "wkswrk": raw.WKSWRK, "weight": raw.WEIGHT,
                      "registered": raw.REGIND == (1 if late else 2),
                      "band": raw.BFNMEMB == (1 if late else 2),
                      # 2021 has a binary gender variable and no sex variable.
                      "female": raw.GENDER == 1 if year == 2021 else raw.SEX == 1,
                      "totinc": raw.TOTINC.where(raw.TOTINC < NOT_AVAILABLE),
                      "wages": raw.WAGES.where(raw.WAGES < NOT_AVAILABLE)})
    # 2006 merges married and common law in MARSTH, so the later years do too.
    marital = {1: "never", 2: "couple", 3: "couple", 4: "separated", 5: "divorced", 6: "widowed"} if late \
        else {1: "divorced", 2: "couple", 3: "separated", 4: "never", 5: "widowed"}
    d["marital"] = raw.MARSTH.map(marital)
    d["area"] = area(raw.CMA)
    d["education"] = raw.HDGREE.where(raw.HDGREE != 4, 3)  # trades and apprenticeship together, as in A1b
    d["ancestry_only"] = raw.ETHDER.isin(INDIGENOUS_ORIGINS[year]) & (raw.ABOID == 6)
    if year == 2006:
        d["marst_legal"] = raw.MARST
    if year == 2021:
        # The guide says 99,999,999 is for people under 15, but adults who have it are the ones with no positive
        # amount, and the file has no zeros. So it is read as no benefit.
        d["covid_erb"] = raw.COVID_ERB.where(raw.COVID_ERB != 88_888_888).replace(99_999_999, 0)
    for i in range(REPLICATES[year][0]):
        d[f"wt{i + 1}"] = raw[f"WT{i + 1}"]
    d = pd.concat([d, groups(d)], axis=1)
    return d


def area(cma):
    return cma.where(cma.isin(LARGE_CMA) | (cma == NOT_CMA), 30).astype(int)


def groups(d):
    """The indicators in A1b. Someone with more than one identity and no registered status has each one set."""
    r, a = d.registered, d.aboid
    return pd.DataFrame({"registered_band": r & d.band, "registered_no_band": r & ~d.band,
                         "first_nations": ~r & a.isin((1, 4)), "metis": ~r & a.isin((2, 4)), "inuit": ~r & a.isin((3, 4)),
                         "other_identity": ~r & (a == 5), "indigenous": r | (a != 6)})


def sample(d):
    """Canadian citizens by birth aged 25 to 64 who speak an official language, with education and household size known."""
    return d[(d.citizen == 1) & d.agegrp.between(9, 16) & d.kol.isin((1, 2, 3)) & (d.hdgree <= 13) & (d.hhsize <= 7)
             & d.marital.notna()]


def load(year, root=RAW):
    return sample(harmonise(read_year(year, root), year))


if __name__ == "__main__":
    download()
    for y in YEARS:
        print(y, len(load(y)))
