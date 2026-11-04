# Proposed site text

For the session that integrates the website. Nothing here has been added to the site.

## Portfolio entry

**Title:** The Indigenous income gap in Canada, 2006 to 2021

**Type and year:** Open data analysis in Python, 2026

**Text:** How the income and wage gap changed from the 2006 Census to 2021, with Statistics Canada's public microdata. Comparing people with the same age, education and other measured characteristics, Indigenous men's wages went from about 25% lower to about 14% lower, and Indigenous women's from about 10% lower to about 4% lower. The people counted as Indigenous also changed between censuses, so this is not one group followed over time, and the write-up measures how much that could matter.

**Links:** Project page, and code at https://github.com/atamalfuzi/canada_indigenous_income_gap

## Project page

### Summary

How much lower are the incomes and wages of Indigenous people in Canada than those of other Canadians with the same age, education, language, marital status, area and household size? And how did that change? I look at four rounds of census data: 2006, 2011, 2016 and 2021, for Canadian citizens by birth aged 25 to 64.

The project starts from an earlier analysis of mine that applied the method of Pendakur and Pendakur (2011) to the 2006 Census. I reproduce that work in Python first, then carry it forward.

The results describe a gap and what goes with it. They don't show what causes it.

### The gap narrowed

Figure: `figures/gaps.png`

Comparing people with the same measured characteristics, Indigenous men's wages were about 25% lower in 2006 and 14% lower in 2021. Indigenous women's were about 10% lower and 4% lower. Most of the change for men came by 2016, and most of the change for women came in 2021. A later paper by Pendakur and Pendakur, using the full census files, finds the same direction.

### What measured characteristics account for

Figures: `figures/decomposition.png`, then `figures/characteristics.png`

Differences in age, education and the other measured characteristics account for roughly a third to a half of the wage gap among men and roughly 60% or more among women. Education is the largest part. The rest of the gap is not a measure of any one cause, and the measured characteristics can themselves reflect earlier disadvantage.

### The average covers very different groups

Figure: `figures/groups.png`

The largest gaps are among registered men who are members of a First Nation or band: about 39% lower wages in 2006 and 26% lower in 2021. The public files can't say who lives on reserve, so this is not a statement about reserves. My earlier analysis had labelled these groups as if it were, and that is corrected here.

### 2021 and the pandemic

Income in the 2021 Census is from 2020 and includes pandemic benefits, which more Indigenous people received. Taking them out removes about two thirds of the narrowing in men's total income between 2016 and 2021, so 2021 should not be read as a new normal.

### Whether these are the same people

Figure: `figures/identity.png`

Following people born in the same years, the comparison group shrinks by about 4% by 2021, as expected. The Indigenous group in the same birth years grows by 28%, because more people report an Indigenous identity or registered status over time. Even if everyone added had the comparison group's income, the men's wage gap in these birth years would still narrow, from 29% to 17%. That is a rough check, not a firm bound.

### Notes for the page

- Use the "Personal project" disclaimer from the README.
- Wherever a number from this project is quoted, keep the statement that the results describe a gap and not its causes, and the caution that the people counted as Indigenous change between censuses.
- Use Indigenous, First Nations, Métis and Inuit in site text. "Aboriginal" appears only in the titles of older sources.
- The tables in the README can be reused as they are. The source numbers are in `output/`, in log points.
