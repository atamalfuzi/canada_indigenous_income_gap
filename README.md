# canada_indigenous_income_gap

[![tests](https://github.com/atamalfuzi/canada_indigenous_income_gap/actions/workflows/tests.yml/badge.svg)](https://github.com/atamalfuzi/canada_indigenous_income_gap/actions/workflows/tests.yml)

How much lower are the incomes and wages of Indigenous people in Canada than those of other Canadians with the same age, education and other measured characteristics, and how did that change from 2006 to 2021? This project answers that with four rounds of Statistics Canada's public census microdata: 2006, 2011, 2016 and 2021. Income in each is from the year before. Python, with pandas and NumPy.

It started as an assignment in a graduate applied econometrics course (ECON 836) at Simon Fraser University. That assignment applied the method of Pendakur and Pendakur (2011) to the 2006 Census. Here the 2006 results are reproduced in Python and the work is carried forward to 2021.

> **Personal project.** This is my own analysis of publicly available data. It is not associated with my work for any current or past employer and does not represent their views.

The results describe a gap and what goes with it in these files. They do not show what causes it. Nothing here measures the abilities, habits or culture of any group.

## In short

- **The gap narrowed.** Comparing people with the same measured characteristics, Indigenous men's wages were about 25% lower in 2006 and about 14% lower in 2021. Indigenous women's wages were about 10% lower in 2006 and about 4% lower in 2021. For men most of the change came by 2016. For women most of it came in 2021.
- **Measured characteristics explain part of the gap.** Differences in age, education, language, marital status, area and household size account for roughly a third to a half of the wage gap among men, and roughly 60% or more among women. Education is the largest part.
- **The average hides large differences.** The largest gaps are among registered men who are members of a First Nation or band: about 39% lower wages in 2006 and 26% lower in 2021.
- **2021 is partly a pandemic year.** Income in the 2021 Census is from 2020 and includes federal pandemic benefits, which more Indigenous people received. Taking them out removes about two thirds of the 2016 to 2021 narrowing in men's total income.
- **The 2006 assignment reproduces closely, though not exactly.** The sample in Python is 0.7% larger, for a reason I could not trace.

## The most important caution

**The people counted as Indigenous are not the same from one census to the next.** Some people report an Indigenous identity in one census and not in the next, in both directions. The laws on who can be registered changed, and so did the questions and which communities took part. A Statistics Canada study that linked people across censuses found that about one in four people reporting an Aboriginal identity in 2016 had not reported one in 2011 (O'Donnell and LaPointe 2019). The public files cannot follow people, so a smaller gap could come from changes in income, from changes in who is counted, or both. [Section 6](#6-are-these-the-same-people-over-time) measures how big the change is and how much it could matter.

The part of the gap that measured characteristics don't account for is not a measure of any one cause. It can include things these files don't measure, such as hours worked, the kind of job, where exactly someone lives, tax treatment, differences in how income is recorded, and discrimination. These data cannot tell them apart.

## Who is compared

Everyone in the results is a Canadian citizen by birth, aged 25 to 64, who speaks English or French and had at least $1,000 of the income being studied. The **Indigenous group** is everyone who reported an Indigenous identity (First Nations, Métis or Inuit) or registered status under the Indian Act. The **comparison group** is everyone else, except people who reported only Indigenous ancestry without an identity, who are set aside.

Two measures are used. **Total income** is income from all sources, including government transfers. **Wages** are wages and salaries from employment.

A gap is how much lower the Indigenous group's typical income is, in per cent. "All people" compares the two groups as they are. "Same characteristics" compares people of the same age group, highest qualification, official language, marital status, area and household size. Each estimate has a margin of error of about 1 to 3 percentage points either way.

## Results

### 1. How did the gap change?

![How much lower Indigenous incomes and wages are, by year](figures/gaps.png)

| Per cent lower than the comparison group | | 2006 | 2011 | 2016 | 2021 |
|---|---|---:|---:|---:|---:|
| Wages, men | All people | 35% | 27% | 25% | 24% |
| | Same characteristics | 25% | 19% | 16% | 14% |
| Wages, women | All people | 28% | 21% | 22% | 19% |
| | Same characteristics | 10% | 7% | 9% | 4% |
| Total income, men | All people | 44% | 37% | 36% | 27% |
| | Same characteristics | 31% | 27% | 25% | 15% |
| Total income, women | All people | 26% | 24% | 24% | 15% |
| | Same characteristics | 9% | 8% | 9% | 1% |

Among men, the wage gap for people with the same characteristics narrowed by 11 percentage points from 2006 to 2021, and most of that had happened by 2016. Among women it narrowed by 6 points. The change for women from 2006 to 2016 alone is too small to tell apart from no change. For total income, the largest step for both men and women is the last one, which [section 4](#4-how-much-is-2021-a-pandemic-result) looks at.

Pendakur and Pendakur's later paper, *Indigenous Earnings Convergence*, uses the full census files in a Statistics Canada research centre and finds the same direction. It reports earnings gaps falling from 36% to 16% for men and from 16% to 6% for women between 1995 and 2020. Their sample, comparison group and starting year are different, so the numbers can't be compared one for one.

**Annual wages mix pay with time worked.** Among people who worked mainly full-time for 49 weeks or more, the gaps are much smaller:

| Wages, same characteristics, per cent lower | 2006 | 2011 | 2016 | 2021 |
|---|---:|---:|---:|---:|
| Men, everyone with wages | 25% | 19% | 16% | 14% |
| Men, full-year full-time workers | 12% | 8% | 6% | 6% |
| Women, everyone with wages | 10% | 7% | 9% | 4% |
| Women, full-year full-time workers | 4% | 5% | 2% | 2% |

So more than half of the men's wage gap is not there among full-year, full-time workers. This compares two groups of people. It doesn't show that working less is a choice, since it also depends on what work is available.

### 2. How much do measured characteristics account for?

![The gap split into the part characteristics account for and the rest](figures/decomposition.png)

This uses an Oaxaca-Blinder decomposition. It asks how much of the gap would remain if the Indigenous group had the same average age, education and other measured characteristics as the comparison group. The answer depends slightly on whose pay patterns are used to value those characteristics, so both versions are shown:

| Share of the gap that characteristics account for | | 2006 | 2011 | 2016 | 2021 |
|---|---|---:|---:|---:|---:|
| Wages, men | Valued at the comparison group's pay patterns | 31% | 31% | 37% | 43% |
| | Valued at the Indigenous group's pay patterns | 49% | 41% | 50% | 54% |
| Wages, women | Comparison group's | 68% | 69% | 64% | 80% |
| | Indigenous group's | 62% | 70% | 66% | 78% |
| Total income, men | Comparison group's | 33% | 31% | 36% | 49% |
| | Indigenous group's | 48% | 51% | 50% | 58% |
| Total income, women | Comparison group's | 72% | 69% | 68% | 96% |
| | Indigenous group's | 59% | 62% | 58% | 78% |

![The part of the gap linked to each characteristic](figures/characteristics.png)

Education is the largest part in every year, and more than half of the part characteristics account for. Area and household size matter less in 2021 than in 2006. Among men, nearly all of the narrowing in the wage gap is in the part that characteristics don't account for.

A characteristic that accounts for part of the gap is not a neutral or settled explanation. Education, where people live, marital status and household size can themselves reflect earlier disadvantage, including discrimination. The decomposition is a way of splitting the numbers, not a prediction of what would happen if any characteristic changed.

### 3. Who does the average cover?

![The gap by group](figures/groups.png)

| Wages, same characteristics, per cent difference | Women 2006 | Women 2021 | Men 2006 | Men 2021 |
|---|---:|---:|---:|---:|
| Registered, member of a First Nation or band | −10% | −6% | −39% | −26% |
| Registered, not a band member | −14% | +1% | −16% | −6% |
| First Nations, not registered | −14% | −8% | −13% | −11% |
| Métis, not registered | −11% | −3% | −8% | −2% |
| Inuit, not registered | +23% | +6% | −18% | −16% |

Each group is compared with the same comparison group. Someone who reported more than one identity counts in each, as in the original assignment. The groups other than Métis and registered band members are small, and their margins of error are about 4 to 25 points. All years, total income and the margins of error are in `output/group_gaps.csv`.

Registered men who are band members have the largest gap in every year. Among women, the same group's gap is close to the others'. Inuit women's incomes are higher than the comparison group's in every year. The area measure doesn't separate the North from the rest of Canada, so this isn't a comparison of people in the same places.

**Band membership is not the same as living on reserve.** The public files have no on-reserve measure, and many band members live off reserve. Pendakur and Pendakur's later paper, which can see where people live, finds much less narrowing for registered people living on reserve than for others. So the narrowing among band members here may come mostly from those living off reserve. As that paper notes, income earned on reserve by registered people can be exempt from income tax, so the same pre-tax income doesn't mean the same thing for them.

Two groups in the output files should not be read as trends. "Other Indigenous identity" has as few as nine people in some cells. "Indigenous ancestry only" is defined differently each year, because the list of ancestries changed, and its size doubles in 2021.

### 4. How much is 2021 a pandemic result?

Income in the 2021 Census is from 2020 and includes federal pandemic benefits such as CERB. In this sample, 38.7% of Indigenous women received a benefit, against 29.1% of the comparison group, and 37.6% of Indigenous men, against 28.5%. Benefits made up 8.5% of Indigenous women's total income and 6.6% of men's, against 4.5% and 3.1% in the comparison group.

| Total income, same characteristics, per cent lower | 2016 | 2021 | 2021 without benefits |
|---|---:|---:|---:|
| Women | 9% | 1% | 6% |
| Men | 25% | 15% | 22% |
| Registered men who are band members | 44% | 27% | 38% |

Taking the benefits out removes about two thirds of the narrowing in men's total income from 2016 to 2021, and about 60% of the narrowing in women's. So the 2021 total income figures should not be read as a new normal. Wages don't include benefits and are a better guide to the trend, though 2020 was a disrupted year for work too.

### 5. Does the 2006 assignment reproduce?

The assignment, called A1b, ran ordinary least squares regressions of log total income and log wages, separately for women and men, with robust standard errors and no survey weights. The Python version follows the same steps and matches the assignment's log exactly through the income cut-off: 175,179 people dropped for citizenship, 314,670 for age, 191 for language and 12,162 for total income under $100.

| | Women, total income | Men, total income | Women, wages | Men, wages |
|---|---:|---:|---:|---:|
| People, assignment | 170,701 | 166,896 | 131,361 | 135,727 |
| People, here | 171,068 | 169,044 | 131,566 | 137,548 |
| R-squared, assignment | 0.159 | 0.168 | 0.152 | 0.140 |
| R-squared, here | 0.163 | 0.174 | 0.159 | 0.149 |

All 32 group estimates are within 0.35 standard errors of the assignment's, and none changes sign. The largest difference is 0.017 log points. The full comparison is in `output/reproduction_2006.csv`.

After the cut-off the samples differ by about 2,500 people, mostly men. The assignment's log shows 2,667 income values that did not read as numbers, where Statistics Canada's file has only 152 "not available" codes. The assignment used a copy of the file converted through R, which I no longer have. Dropping the highest incomes does not reproduce its numbers, so I don't know the cause. The code here reads Statistics Canada's file directly.

**A correction to the assignment.** It labelled two groups "registered on reserve" and "registered off reserve". They are actually defined by band membership, since the public files have no on-reserve measure. They are named for what they are here.

To compare across years, the model has to use only variables that exist in every census. Three things change from the assignment: marital status uses a version available in every year, detailed ethnic-origin controls are dropped because the list of origins changes each census, and people with mixed Indigenous and other ancestry stay in the comparison group because later files don't identify them. On 2006 data these changes move the group estimates by 0.053 log points at most.

### 6. Are these the same people over time?

A group of people born in the same years should shrink slightly from one census to the next as people die or move away. The comparison group does. Following people born in Canada who were 25 to 44 in 2006:

![Counts of the same birth years at each census, relative to 2006](figures/identity.png)

| Count compared with 2006 | 2011 | 2016 | 2021 |
|---|---:|---:|---:|
| Comparison group | 1.00 | 0.98 | 0.96 |
| Indigenous identity or registered | 1.04 | 1.22 | 1.28 |
| Registered | 0.95 | 1.07 | 1.09 |
| First Nations, not registered | 1.50 | 1.53 | 1.85 |
| Métis, not registered | 1.08 | 1.43 | 1.51 |
| Inuit, not registered | 0.95 | 1.08 | 1.12 |

By 2021, about a quarter of the Indigenous group in these birth years was not counted as Indigenous in 2006. Some of the growth in registered status can follow changes in the law, including Bills C-31, C-3 and S-3 and the recognition of the Qalipu Mi'kmaq First Nation in 2011. The communities taking part also changed. Statistics Canada says these influences can't be separated.

The gap within these same birth years narrowed too. A simple what-if gives a sense of how much changed reporting could matter. Suppose everyone added to the group since 2006 had the comparison group's income, so the people counted in 2006 carry the whole gap:

| Same birth years, same characteristics, per cent lower | 2006 | 2021 | 2021 in the what-if |
|---|---:|---:|---:|
| Wages, men | 29% | 13% | 17% |
| Wages, women | 10% | 5% | 6% |
| Total income, men | 33% | 15% | 20% |
| Total income, women | 6% | 6% | 7% |

Even then the men's wage gap narrows, from 29% to 17%. This is only a rough check. It uses the net change, while the Statistics Canada study shows that many more people move in and out than the net suggests. It says nothing about the people who stopped reporting, whose incomes can't be seen. And gaps change with age, so these rows mix getting older with change over time.

## Other cautions

- **2011 is a different kind of survey.** The 2011 National Household Survey was voluntary, and 68.6% of households responded, against 95.7% for the 2021 long-form census. It is shown with a hollow point in the charts.
- **Coverage of reserves changes.** The number of reserves and settlements not fully counted was 22 in 2006, 36 in 2011, 14 in 2016 and 63 in 2021. The public files can't restrict to communities counted in every year, as Statistics Canada advises. In 2021, 23.1% of people living on reserve did not respond to the long form.
- **Where income data come from changed.** In 2006 and 2011, people could report income on the form or let Statistics Canada use their tax records. In 2016 and 2021, income comes only from tax and benefit records. Among people on reserves and in remote areas, the share matched to such a record fell from 82% in 2016 to 67% in 2021, and income for people not matched is filled in statistically. This may matter most for registered band members, whose total income gap moved the most.
- **People without income or wages are left out.** The share of Indigenous people with at least $1,000 in wages is lower than in the comparison group, and that difference did not shrink: 8.0 percentage points among men in 2006 and 9.1 in 2021, and 8.1 and 10.3 among women. The gaps above are among people with wages.
- **Incomes are rounded and capped.** To protect privacy, every file rounds income to the nearest $1,000 ($10,000 above $100,000) and replaces very high incomes with group averages. So the $100 cut-off from the assignment works as a $1,000 cut-off.
- **Sex and gender.** The 2021 file records gender as woman or man and has no sex variable. Earlier files record sex.
- **The area measure is broad.** It separates 11 large cities, a group of smaller cities, and the rest of Canada. It has no province, North or reserve breakdown.
- **Some people are outside the sample.** People in institutions or other collective housing, people who speak neither English nor French, and anyone who is not a citizen by birth are left out.
- **Terms.** Statistics Canada's variable is "Registered or Treaty Indian status", a legal term under the Indian Act. I write "registered". Older sources say "Aboriginal", which I keep only in their titles and when reporting what they found.

## How it was done

- **Gaps.** Weighted least squares regressions of log income or log wages on an Indigenous indicator and the six sets of characteristics, run separately for women and men in each year. A coefficient b is turned into a per cent with 100 × (e^b − 1). The log-point estimates and standard errors are in `output/gaps.csv`.
- **Margins of error.** Standard errors use the replicate weights in each file and the method in each user guide: 8 groups in 2006 and 2011, and 16 groups in 2016 and 2021, with the 2021 adjustment. Ordinary robust standard errors, in `output/sensitivity.csv`, are of similar size, and none of the changes described above depends on which is used.
- **Decomposition.** A two-fold Oaxaca-Blinder decomposition with each group's coefficients in turn. The part linked to each characteristic adds up its categories, so it doesn't depend on which category is left out.
- **Groups.** The indicators from the assignment, entered together in one regression with the same characteristics.
- **Pandemic check.** Total income less the 2021 file's emergency and recovery benefits variable.
- **Same birth years.** Weighted counts of people born in Canada who were aged 25 to 44 in 2006, 30 to 49 in 2011, 35 to 54 in 2016 and 40 to 59 in 2021.

## Run it

The census files are not in this repository. `data.py` downloads four zip files from Statistics Canada, about 460 MB, into `data/`.

```bash
python -m venv .venv
```

```bash
.venv/Scripts/pip install -r requirements-dev.txt
```

```bash
.venv/Scripts/python data.py
```

```bash
.venv/Scripts/python estimate.py
```

```bash
.venv/Scripts/python figures.py
```

```bash
.venv/Scripts/pytest
```

On Linux or macOS use `.venv/bin/` instead of `.venv/Scripts/`. The estimation takes a few minutes. The tests don't need the census files.

| File | What it does |
|---|---|
| `data.py` | Downloads the files, reads each year's layout and puts the codes on one scheme |
| `estimate.py` | Reproduces the 2006 assignment, then writes the gap, decomposition, group, sensitivity and same-birth-year tables to `output/` |
| `figures.py` | Draws the charts in `figures/` |
| `tests/` | Checks the code mappings, the regressions against statsmodels, that the decomposition adds up, the margin-of-error formula and the reproduction |
| `SITE.md` | Proposed text for a portfolio page |

## Sources

Data are used under the [Statistics Canada Open Licence](https://www.statcan.gc.ca/eng/reference/licence). Adapted from Statistics Canada. This does not constitute an endorsement by Statistics Canada of this product. All four files are listed on the [public use microdata files page](https://www150.statcan.gc.ca/n1/pub/98m0001x/index-eng.htm).

| Year | Source | Catalogue | File |
|---|---|---|---|
| 2006 | Census, individuals file | 95M0028X | [`cen06_ind_95m0028x_part_rec06.zip`](https://www150.statcan.gc.ca/n1/pub/98m0001x/2023001/cen06_ind_95m0028x_part_rec06.zip) |
| 2011 | National Household Survey, individuals file | 99M0001X | [`nhs11_ind_99m0001x_part_enm11.zip`](https://www150.statcan.gc.ca/n1/pub/98m0001x/2023001/nhs11_ind_99m0001x_part_enm11.zip) |
| 2016 | Census, individuals file | 98M0001X | [`cen16_ind_98m0001x_part_rec16.zip`](https://www150.statcan.gc.ca/n1/pub/98m0001x/2023001/cen16_ind_98m0001x_part_rec16.zip) |
| 2021 | Census, individuals file | 98M0001X | [`cen21_ind_98m0001x_part_rec21.zip`](https://www150.statcan.gc.ca/n1/pub/98m0001x/2023001/cen21_ind_98m0001x_part_rec21.zip) |

Files for 1991, 1996 and 2001 are also available. They aren't used here, since the assignment started at 2006 and their codes would need a separate review.

Notes on comparability come from the user guides and reference guides inside each zip, especially the 2021 Indigenous Peoples and Income reference guides.

- O'Donnell, V. and R. LaPointe (2019). [Response mobility and the growth of the Aboriginal identity population, 2006-2011 and 2011-2016](https://www150.statcan.gc.ca/n1/pub/99-011-x/99-011-x2019002-eng.htm). Statistics Canada, catalogue 99-011-X.
- Pendakur, K. and R. Pendakur (2011). [Aboriginal Income Disparity in Canada](https://ideas.repec.org/a/cpp/issued/v37y2011i1p61-83.html). *Canadian Public Policy* 37(1), 61-83.
- Pendakur, K. and R. Pendakur. [Indigenous Earnings Convergence: Canada 1995 to 2020](https://www.sfu.ca/~pendakur/papers/Indigenous%20Earnings%20Convergence.pdf). Working paper.
- The original assignment: [`Applied Econometrics/A1b`](https://github.com/atamalfuzi/economics_coursework/tree/main/Applied%20Econometrics/A1b) in economics_coursework.

## License

Code is under the MIT License. See [LICENSE](LICENSE).
