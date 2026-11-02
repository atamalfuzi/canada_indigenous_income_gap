# Proposed site text

For the session that integrates the website. Nothing here has been added to the site. The repository is not public yet, so the code link will not work until it is.

## Portfolio entry

**Title:** The Indigenous income gap in Canada across four censuses, and what can be said about it

**Type and year:** Open data analysis in Python, 2026

**Text:** An extension of a graduate econometrics assignment from the 2006 Census to 2021, on Statistics Canada's public microdata. Among people with the same measured characteristics, the wage gap narrowed from about 25% to about 14% for men and from about 10% to about 4% for women. The people counted as Indigenous also changed across these files, so this is not one group followed over time, and the write-up measures how far that could matter.

**Links:** Project page, and code at https://github.com/atamalfuzi/canada_indigenous_income_gap

## Project page

### Summary

I compare the income and wages of Indigenous and non-Indigenous Canadians with the same age group, education, official languages, marital status, area and household size, in four files: the 2006 Census, the 2011 National Household Survey, and the 2016 and 2021 Censuses. The sample is Canadian citizens by birth aged 25 to 64. It starts by reproducing a course assignment that applied Pendakur and Pendakur (2011) to 2006.

This describes a gap and what it is correlated with in these files. It does not identify causes.

### How the gap changed

Figure: `figures/gaps.png`

Among men, the adjusted wage gap went from −0.287 log points in 2006 to −0.152 in 2021. Among women, it went from −0.107 to −0.043, most of that in the last step. The direction agrees with Pendakur and Pendakur's later work on the full census files.

### What observed characteristics account for

Figures: `figures/decomposition.png`, then `figures/characteristics.png`

A decomposition puts the share of the raw wage gap accounted for by measured characteristics at 31% to 54% among men and 62% to 80% among women, depending on the year and whose coefficients are used. Education is the largest part. The rest is not a measure of any one cause, and the measured characteristics can themselves reflect earlier disadvantage.

### The average covers very different groups

Figure: `figures/groups.png`

The largest gaps are among registered men who are band members: −0.50 in wages in 2006 and −0.30 in 2021. The public files have no on-reserve variable, so this is not a statement about reserves. The assignment's labels had suggested it was, and that is corrected here.

### 2021 and the pandemic

Income in the 2021 file is from 2020 and includes pandemic benefits, which more Indigenous people received. Taking them out moves the adjusted total income gap for men from −0.158 to −0.243, so total income in 2021 should not be read as a new level.

### Whether these are the same people

Figure: `figures/identity.png`

People aged 25 to 44 in 2006 are counted again at each later census. The comparison group shrinks by 4% by 2021, while the Indigenous group in the same birth years grows by 28%. Changes in reporting, law and coverage cannot be separated here. If every net addition had the comparison group's income, the wage gap among men in these birth years would still narrow, from −0.336 to −0.187, but this uses net change only and is not a true bound.

### Notes for the page

- Use the "Personal project" disclaimer from the README.
- Keep the statement that the results describe correlates and not causes, and the first limit from the README, wherever a number from this project is quoted.
- Use Indigenous, First Nations, Métis and Inuit in site text. "Aboriginal" appears only in the titles of older sources.
- The tables in the README can be reused as they are. The source numbers are in `output/`.
