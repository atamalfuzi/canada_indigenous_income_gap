"""Reproduce the 2006 regressions from A1b, estimate the gap in every year, and write every table the README quotes to output/."""
import numpy as np
import pandas as pd

from data import NOT_AVAILABLE, OUTPUT, RAW, REPLICATES, YEARS, harmonise, read_year, sample

FLOOR = 100  # dollars, from A1b. Income is rounded to $1,000 in all four files, so this keeps $1,000 and above.
OUTCOMES = {"totinc": "Total income", "wages": "Wages"}
SEXES = {"women": True, "men": False}
CONTROLS = {"age": "agegrp", "education": "education", "language": "kol", "marital status": "marital", "area": "area",
            "household size": "hhsize"}
GROUPS = {"registered_band": "Registered, band member", "registered_no_band": "Registered, not a band member",
          "first_nations": "First Nations, not registered", "metis": "Métis, not registered",
          "inuit": "Inuit, not registered", "other_identity": "Other Indigenous identity, not registered",
          "ancestry_only": "Indigenous ancestry only"}
# The same people in each file: aged 25 to 44 in 2006, five years older at each census. AGEGRP steps by five years in this range.
COHORT = {2006: range(9, 13), 2011: range(10, 14), 2016: range(11, 15), 2021: range(12, 16)}
COHORT_GROUPS = {"Indigenous identity or registered": "indigenous", "Registered": "registered",
                 "First Nations, not registered": "first_nations", "Métis, not registered": "metis",
                 "Inuit, not registered": "inuit", "Comparison group": "comparison"}

# A1b_results.pdf: coefficient and standard error, in the order of GROUPS with multiple ancestry added at the end.
PUBLISHED = {
    ("totinc", "women"): (170701, .1592, [(-.140855, .016044), (-.117455, .058394), (-.098363, .030906), (-.086033, .018917),
                                          (.210371, .055044), (-.326923, .114456), (-.139551, .042507), (-.064978, .014578)]),
    ("totinc", "men"): (166896, .1678, [(-.5902211, .0212554), (-.1911139, .0621299), (-.1739621, .0366144), (-.1446409, .0199557),
                                        (-.1859929, .0717780), (-.3169380, .1288622), (-.0977290, .0465546), (-.1050061, .0164686)]),
    ("wages", "women"): (131361, .1522, [(-.111597, .0206977), (-.159866, .0805282), (-.149073, .0437187), (-.123782, .0239304),
                                         (.192986, .0757331), (-.459121, .1678293), (-.213001, .0563280), (-.079196, .0179859)]),
    ("wages", "men"): (135727, .1404, [(-.478809, .022838), (-.162601, .065448), (-.100155, .040508), (-.075636, .021705),
                                       (-.171847, .070687), (-.121693, .101879), (.010260, .042751), (-.088878, .018309)]),
}


def dummies(column):
    """Indicators for all but the first category."""
    return pd.get_dummies(column, prefix=column.name, dtype=float).iloc[:, 1:]


def wls(y, x, w=None):
    """Coefficients. A category empty in a small replicate gets the minimum-norm solution rather than an error."""
    w = np.ones(len(y)) if w is None else w
    return np.linalg.lstsq((x * w[:, None]).T @ x, (x * w[:, None]).T @ y, rcond=None)[0]


def hc1(y, x):
    """Least squares with the standard errors of Stata's reg, robust."""
    n, k = x.shape
    inverse = np.linalg.inv(x.T @ x)
    beta = inverse @ (x.T @ y)
    e = y - x @ beta
    return beta, np.sqrt(np.diag(inverse @ ((x * e[:, None] ** 2).T @ x) @ inverse) * n / (n - k)), 1 - e @ e / ((y - y.mean()) ** 2).sum()


def with_outcome(d, outcome):
    y = d[outcome]
    return d[y.between(FLOOR, NOT_AVAILABLE - 1)].assign(y=lambda f: np.log(f[outcome]))


def replicate_se(point_function, d, year):
    """An estimate and its standard error by the random groups method in each year's user guide."""
    groups, divisor = REPLICATES[year]
    estimate = point_function(d, d.weight.to_numpy())
    reps = pd.DataFrame([point_function(d, d[f"wt{i + 1}"].to_numpy()) for i in range(groups)])
    return estimate, np.sqrt(((reps - reps.mean()) ** 2).sum() / divisor)


def control_matrix(d):
    """A constant and indicators for the six control families, and which columns belong to which family."""
    parts = {family: dummies(d[column].astype(str).rename(column)) for family, column in CONTROLS.items()}
    x = np.column_stack([np.ones(len(d))] + [p.to_numpy() for p in parts.values()])
    edges = np.cumsum([1] + [p.shape[1] for p in parts.values()])
    return x, {family: slice(edges[i], edges[i + 1]) for i, family in enumerate(parts)}


def pooled(d):
    """People with Indigenous identity or registered status, and the comparison group. Ancestry only is in neither."""
    return d[d.indigenous | ~d.ancestry_only]


def gap_function(d):
    """Raw and adjusted gaps and the decomposition. The gap is Indigenous less comparison, so negative is lower."""
    x, families = control_matrix(d)
    y, indigenous = d.y.to_numpy(), d.indigenous.to_numpy()
    with_group = np.column_stack([indigenous.astype(float), x])

    def estimates(_, w):
        keep = w > 0
        wi, wc = w * indigenous, w * ~indigenous
        mean_i, mean_c = (x * wi[:, None]).sum(0) / wi.sum(), (x * wc[:, None]).sum(0) / wc.sum()
        raw = (y * wi).sum() / wi.sum() - (y * wc).sum() / wc.sum()
        beta_c = wls(y[keep & ~indigenous], x[keep & ~indigenous], w[keep & ~indigenous])
        parts = {family: (mean_i - mean_c)[s] @ beta_c[s] for family, s in families.items()}
        explained = sum(parts.values())
        adjusted = wls(y[keep], with_group[keep], w[keep])[0]
        return pd.Series({"raw": raw, "adjusted": adjusted, "explained": explained, "unexplained": raw - explained, **parts})
    return estimates


def other_weights(d):
    """The same decomposition with the Indigenous group's coefficients, which answers the question the other way round."""
    x, _ = control_matrix(d)
    w, y, indigenous = d.weight.to_numpy(), d.y.to_numpy(), d.indigenous.to_numpy()
    wi, wc = w * indigenous, w * ~indigenous
    difference = (x * wi[:, None]).sum(0) / wi.sum() - (x * wc[:, None]).sum(0) / wc.sum()
    return difference @ wls(y[indigenous], x[indigenous], w[indigenous])


def group_function(d):
    """The A1b indicators together, with the controls."""
    x, _ = control_matrix(d)
    x = np.column_stack([d[list(GROUPS)].to_numpy(float), x])
    y = d.y.to_numpy()
    return lambda _, w: pd.Series(wls(y[w > 0], x[w > 0], w[w > 0])[:len(GROUPS)], index=list(GROUPS))


def a1b_regressions(d):
    """A1b as written on the 2006 file: unweighted, with legal marital status and detailed origins."""
    rows = []
    a1b = d.assign(multiple=(d.aboid == 6) & d.ethder.isin((48, 49, 50)),
                   origin=d.ethder.where((d.aboid == 6) & d.ethder.between(10, 46), 0).astype(int))
    for outcome in OUTCOMES:
        for sex, flag in SEXES.items():
            s = with_outcome(a1b[a1b.female == flag], outcome)
            controls = [dummies(s[c].astype(int).rename(c)) for c in ("agegrp", "education", "kol", "marst_legal", "area", "hhsize", "origin")]
            names = [*GROUPS, "multiple"]
            x = np.column_stack([s[names].to_numpy(float), np.ones(len(s)), *[c.to_numpy() for c in controls]])
            beta, se, r2 = hc1(s.y.to_numpy(), x)
            n, published_r2, published = PUBLISHED[outcome, sex]
            for i, name in enumerate(names):
                rows.append({"outcome": outcome, "sex": sex, "group": name, "coefficient": beta[i], "se": se[i],
                             "published": published[i][0], "published_se": published[i][1], "n": len(s), "published_n": n,
                             "r2": r2, "published_r2": published_r2})
    return pd.DataFrame(rows).assign(difference_in_se=lambda t: (t.coefficient - t.published) / t.published_se)


def year_tables(d, year):
    """Gaps, decomposition and group gaps by outcome and sex for one year."""
    gaps, groups = [], []
    for outcome in OUTCOMES:
        for sex, flag in SEXES.items():
            s = with_outcome(d[d.female == flag], outcome)
            p = pooled(s)
            estimate, se = replicate_se(gap_function(p), p, year)
            gaps.append({"year": year, "outcome": outcome, "sex": sex, "n_indigenous": int(p.indigenous.sum()),
                         "n_comparison": int((~p.indigenous).sum()), **estimate, **se.add_suffix("_se"),
                         "explained_other": other_weights(p)})
            estimate, se = replicate_se(group_function(s), s, year)
            groups += [{"year": year, "outcome": outcome, "sex": sex, "group": g, "gap": estimate[g], "se": se[g],
                        "n": int(s[g].sum())} for g in GROUPS]
    return gaps, groups


def adjusted_gap(d, year, label, outcome="totinc", sex="women", weighted=True):
    """The adjusted gap on a changed sample or outcome, for the sensitivity table."""
    p = pooled(d)
    if weighted:
        estimate, se = replicate_se(gap_function(p), p, year)
        return {"check": label, "year": year, "outcome": outcome, "sex": sex, "adjusted": estimate.adjusted, "se": se.adjusted}
    x = np.column_stack([p.indigenous.to_numpy(float), control_matrix(p)[0]])
    beta, robust, _ = hc1(p.y.to_numpy(), x)
    return {"check": label, "year": year, "outcome": outcome, "sex": sex, "adjusted": beta[0], "se": robust[0]}


def full_year_full_time(d, year):
    return (d.fptwk == 1) & (d.wkswrk.between(49, 52) if year == 2006 else d.wkswrk == 6)


def sensitivity(d, year):
    rows = []
    for sex, flag in SEXES.items():
        people = d[d.female == flag]
        for outcome in OUTCOMES:
            s = with_outcome(people, outcome)
            rows.append(adjusted_gap(s, year, "Unweighted", outcome, sex, weighted=False))
            rows.append(adjusted_gap(s[s.agegrp.isin(COHORT[year])], year, "Same birth years (aged 25 to 44 in 2006)", outcome, sex))
            if year == 2006:
                rows.append(adjusted_gap(s[~((s.aboid == 6) & s.ethder.isin((48, 49, 50)))], year,
                                         "Mixed Indigenous ancestry out of the comparison group", outcome, sex))
        rows.append(adjusted_gap(with_outcome(people[full_year_full_time(people, year)], "wages"), year,
                                 "Full-year, full-time workers", "wages", sex))
        if year == 2021:
            less = people.assign(no_covid=people.totinc - people.covid_erb)
            rows.append(adjusted_gap(with_outcome(less, "no_covid"), year, "Total income less pandemic benefits", "totinc", sex))
    return rows


def floor_shares(d, year):
    """Share of each group with at least $1,000, the people the log regressions can use."""
    rows = []
    for outcome in OUTCOMES:
        for sex, flag in SEXES.items():
            s = pooled(d[d.female == flag])
            above = s[outcome].between(FLOOR, NOT_AVAILABLE - 1)
            for group, members in (("Indigenous", s.indigenous), ("Comparison group", ~s.indigenous)):
                rows.append({"year": year, "outcome": outcome, "sex": sex, "group": group,
                             "share": (above * s.weight)[members].sum() / s.weight[members].sum()})
    return rows


def pandemic_benefits(d):
    """In 2021, who had a benefit and how much of total income it was, among people with the $1,000 floor met."""
    rows = []
    for sex, flag in SEXES.items():
        s = pooled(with_outcome(d[d.female == flag], "totinc"))
        for group, members in (("Indigenous", s.indigenous), ("Comparison group", ~s.indigenous)):
            m = s[members]
            rows.append({"sex": sex, "group": group, "share_with_benefit": (m.weight * (m.covid_erb > 1)).sum() / m.weight.sum(),
                         "benefit_share_of_income": (m.weight * m.covid_erb).sum() / (m.weight * m.totinc).sum()})
    return pd.DataFrame(rows)


def groups_less_benefits(d):
    """The group gaps in 2021 with pandemic benefits taken out of total income."""
    rows = []
    for sex, flag in SEXES.items():
        s = d[d.female == flag]
        s = with_outcome(s.assign(no_covid=s.totinc - s.covid_erb), "no_covid")
        estimate, se = replicate_se(group_function(s), s, 2021)
        rows += [{"sex": sex, "group": g, "gap": estimate[g], "se": se[g]} for g in GROUPS]
    return pd.DataFrame(rows)


def cohort_counts(everyone, year):
    """Weighted counts of the same birth years, born in Canada, of both sexes, with no income or language conditions."""
    d = everyone[(everyone.citizen == 1) & everyone.agegrp.isin(COHORT[year])]
    d = d.assign(comparison=~d.indigenous & ~d.ancestry_only)

    def count(frame, w):
        return pd.Series({label: w[frame[c].to_numpy()].sum() for label, c in COHORT_GROUPS.items()})
    estimate, se = replicate_se(count, d, year)
    return [{"year": year, "group": g, "count": estimate[g], "se": se[g]} for g in COHORT_GROUPS]


def identity_bound(cohorts, same_birth_years):
    """If the net addition to the cohort had the comparison group's income, what would the first group's gap have been?"""
    wide = cohorts.pivot(index="year", columns="group", values="count")
    any_group, comparison = wide["Indigenous identity or registered"], wide["Comparison group"]
    expected = any_group[2006] * comparison / comparison[2006]  # what the count would be had it shrunk like the comparison group
    added = (1 - expected / any_group).rename("net_added_share")
    gaps = same_birth_years.merge(added.reset_index(), on="year")
    return gaps.assign(gap_if_added_at_comparison_level=lambda t: t.adjusted / (1 - t.net_added_share))


def changes(gaps):
    """2021 less 2006, and 2016 less 2006 to leave the pandemic year out."""
    rows = []
    for (outcome, sex), t in gaps.groupby(["outcome", "sex"]):
        t = t.set_index("year")
        for last in (2016, 2021):
            for measure in ("raw", "adjusted", "unexplained"):
                change = t.loc[last, measure] - t.loc[2006, measure]
                se = np.hypot(t.loc[last, f"{measure}_se"], t.loc[2006, f"{measure}_se"])
                rows.append({"outcome": outcome, "sex": sex, "from": 2006, "to": last, "measure": measure, "change": change, "se": se})
    return pd.DataFrame(rows)


def run(root=RAW):
    OUTPUT.mkdir(exist_ok=True)
    gaps, groups, checks, floors, cohorts = [], [], [], [], []
    for year in YEARS:
        print("estimating", year, flush=True)
        everyone = harmonise(read_year(year, root), year)
        d = sample(everyone)
        if year == 2006:
            a1b_regressions(d).to_csv(OUTPUT / "reproduction_2006.csv", index=False)
        g, grp = year_tables(d, year)
        gaps += g
        groups += grp
        checks += sensitivity(d, year)
        floors += floor_shares(d, year)
        cohorts += cohort_counts(everyone, year)
        if year == 2021:
            pandemic_benefits(d).to_csv(OUTPUT / "pandemic_benefits.csv", index=False)
            groups_less_benefits(d).to_csv(OUTPUT / "group_gaps_less_benefits.csv", index=False)
    gaps, checks = pd.DataFrame(gaps), pd.DataFrame(checks)
    cohorts = pd.DataFrame(cohorts)
    cohorts["ratio_to_2006"] = cohorts["count"] / cohorts.groupby("group")["count"].transform("first")
    gaps.to_csv(OUTPUT / "gaps.csv", index=False)
    pd.DataFrame(groups).to_csv(OUTPUT / "group_gaps.csv", index=False)
    checks.to_csv(OUTPUT / "sensitivity.csv", index=False)
    pd.DataFrame(floors).to_csv(OUTPUT / "floor_shares.csv", index=False)
    cohorts.to_csv(OUTPUT / "identity_cohorts.csv", index=False)
    changes(gaps).to_csv(OUTPUT / "changes.csv", index=False)
    same = checks[checks.check.str.startswith("Same birth years")]
    identity_bound(cohorts, same).to_csv(OUTPUT / "identity_bound.csv", index=False)


if __name__ == "__main__":
    pd.options.display.float_format = "{:.3f}".format
    run()
    print(pd.read_csv(OUTPUT / "gaps.csv")[["year", "outcome", "sex", "raw", "adjusted", "explained", "unexplained", "explained_other"]])
