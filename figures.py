"""Draw the charts: the gap by year, how much characteristics account for, the gap by group, and identity reporting."""
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data import FIGURES, OUTPUT, YEARS
from estimate import CONTROLS, OUTCOMES, SEXES

INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
                     "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": MUTED,
                     "axes.titlecolor": INK, "axes.titlesize": 11, "axes.grid": True, "grid.color": GRID,
                     "axes.axisbelow": True, "legend.frameon": False})
SOURCE = "Source: Statistics Canada, individuals public use microdata files, 2006, 2011 (National Household Survey), 2016 and 2021."
SAMPLE = "Census years; income is from the year before. Canadian citizens by birth aged 25 to 64 who speak an official language."
INCOME_YEARS = ["2005", "2010", "2015", "2020"]


def save(fig, name, title, subtitle, caption):
    fig.text(0.015, 0.985, title, fontsize=15, fontweight="bold", color=INK, va="top")
    fig.text(0.015, 0.945, subtitle, color=MUTED, va="top")
    fig.text(0.015, 0.012, "\n".join(textwrap.wrap(caption, 138)), color=MUTED, fontsize=9, va="bottom")
    fig.savefig(FIGURES / name, dpi=200, facecolor="white")
    plt.close(fig)


def percent(log_gap):
    """A gap in logs as a per cent difference: -0.15 becomes -13.9."""
    return 100 * np.expm1(log_gap)


def panels(height=8.2, top=0.86, bottom=0.235, ylabel="Per cent difference"):
    """Women and men across, total income and wages down, on one scale."""
    fig, axes = plt.subplots(2, 2, figsize=(10, height), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.085, right=0.975, top=top, bottom=bottom, hspace=0.16, wspace=0.07)
    for (i, outcome), (j, sex) in ((a, b) for a in enumerate(OUTCOMES) for b in enumerate(SEXES)):
        axes[i, j].set_title(f"{OUTCOMES[outcome]}, {sex}", loc="left", fontweight="bold")
        axes[i, j].axhline(0, color=MUTED, lw=1)
    for i in range(2):
        axes[i, 0].set_ylabel(ylabel)
    return fig, axes


def cell(axes, outcome, sex):
    return axes[list(OUTCOMES).index(outcome), list(SEXES).index(sex)]


def line(ax, t, y, se, colour, label):
    """A line in per cent with two standard errors at each point. The 2011 point is hollow because it comes from a voluntary survey."""
    middle, low, high = percent(t[y]), percent(t[y] - 2 * t[se]), percent(t[y] + 2 * t[se])
    ax.errorbar(t.year, middle, yerr=[middle - low, high - middle], color=colour, lw=2, capsize=0, elinewidth=1, label=label, zorder=2)
    ax.scatter(t.year, middle, s=45, color=[("white" if x == 2011 else colour) for x in t.year], edgecolor=colour, linewidth=1.6, zorder=3)


def gaps():
    g, checks = pd.read_csv(OUTPUT / "gaps.csv"), pd.read_csv(OUTPUT / "sensitivity.csv")
    fig, axes = panels()
    for (outcome, sex), t in g.groupby(["outcome", "sex"]):
        ax = cell(axes, outcome, sex)
        line(ax, t, "raw", "raw_se", ORANGE, "All people")
        line(ax, t, "adjusted", "adjusted_se", BLUE, "People with the same age, education, language, marital status, area and household size")
    for sex in SEXES:
        row = checks[(checks.check == "Total income less pandemic benefits") & (checks.sex == sex)].iloc[0]
        ax = cell(axes, "totinc", sex)
        ax.scatter(2021, percent(row.adjusted), marker="D", s=40, color=MAGENTA, zorder=4, label="Same characteristics, total income less pandemic benefits")
    ax = axes[0, 1]
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.075, 0.095), ncol=1, labelcolor=MUTED, fontsize=9.5, handlelength=1.4, borderaxespad=0)
    for ax in axes.flat:
        ax.set_xticks(YEARS)
    save(fig, "gaps.png", "The gap narrowed for men; for women it moved mostly in 2021",
         "How much lower Indigenous people's income and wages are than the comparison group's, in per cent",
         f"{SAMPLE} Income of $1,000 or more. Vertical bars show the margin of error, two standard errors either way. The hollow 2011 point is a voluntary survey. "
         f"The people reporting an identity changed across these years, so this is not one group followed over time. {SOURCE}")


def decomposition():
    g = pd.read_csv(OUTPUT / "gaps.csv")
    fig, axes = panels(bottom=0.19, ylabel="Log points (−0.1 is about 10% lower)")
    for (outcome, sex), t in g.groupby(["outcome", "sex"]):
        ax = cell(axes, outcome, sex)
        ax.bar(t.year, t.explained, width=3.2, color=BLUE, edgecolor="white", linewidth=1.5, label="Accounted for by the measured characteristics")
        ax.bar(t.year, t.unexplained, width=3.2, bottom=t.explained, color=YELLOW, edgecolor="white", linewidth=1.5, label="Left over")
        for r in t.itertuples():
            ax.text(r.year, r.raw - 0.012, f"{r.explained / r.raw:.0%}", ha="center", va="top", color=MUTED, fontsize=9.5)
        ax.set_xticks(YEARS)
    axes[0, 0].set_ylim(-0.68, 0.02)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.075, 0.1), ncol=2, labelcolor=MUTED, fontsize=9.5, handlelength=1.4, borderaxespad=0)
    save(fig, "decomposition.png", "Measured characteristics account for more of the gap among women",
         "Raw gap split with the comparison group's coefficients. The number is the share accounted for.",
         f"{SAMPLE} The left-over part is not a measure of any one cause, and the characteristics may themselves reflect "
         f"earlier disadvantage. {SOURCE}")


def characteristics():
    g = pd.read_csv(OUTPUT / "gaps.csv")
    fig, axes = plt.subplots(2, 2, figsize=(10, 8.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.15, right=0.975, top=0.86, bottom=0.2, hspace=0.16, wspace=0.07)
    families = list(CONTROLS)
    positions = np.arange(len(families))[::-1]
    for (outcome, sex), t in g.groupby(["outcome", "sex"]):
        ax = cell(axes, outcome, sex)
        ax.set_title(f"{OUTCOMES[outcome]}, {sex}", loc="left", fontweight="bold")
        ax.axvline(0, color=MUTED, lw=1)
        for year, colour, shift in ((2006, ORANGE, 0.19), (2021, BLUE, -0.19)):
            row = t[t.year == year].iloc[0]
            ax.barh(positions + shift, [row[f] for f in families], height=0.34, color=colour, label=str(year))
        ax.set_yticks(positions, [f.capitalize() for f in families])
        ax.grid(axis="y", visible=False)
    for ax in axes[1]:
        ax.set_xlabel("Log points (−0.1 is about 10% lower)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.14, 0.1), ncol=2, labelcolor=MUTED, handlelength=1.4, borderaxespad=0)
    save(fig, "characteristics.png", "Education is the largest measured difference in every panel",
         "Part of the raw gap attributed to each set of characteristics, 2006 and 2021",
         f"{SAMPLE} Negative means the difference in that characteristic goes with a lower average for the Indigenous group, "
         f"at the comparison group's coefficients. It describes a statistical split and not a cause. {SOURCE}")


def groups():
    t = pd.read_csv(OUTPUT / "group_gaps.csv")
    shown = {"registered_band": ("Registered, band member", BLUE), "registered_no_band": ("Registered, not a band member", ORANGE),
             "first_nations": ("First Nations, not registered", AQUA), "metis": ("Métis, not registered", YELLOW),
             "inuit": ("Inuit, not registered", MAGENTA)}
    fig, axes = panels()
    for (outcome, sex), part in t.groupby(["outcome", "sex"]):
        ax = cell(axes, outcome, sex)
        for group, (label, colour) in shown.items():
            one = part[part.group == group]
            ax.plot(one.year, percent(one.gap), color=colour, lw=2, label=label, zorder=2)
            ax.scatter(one.year, percent(one.gap), s=38, color=[("white" if x == 2011 else colour) for x in one.year], edgecolor=colour, linewidth=1.6, zorder=3)
        ax.set_xticks(YEARS)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.075, 0.1), ncol=3, labelcolor=MUTED, fontsize=9.5, handlelength=1.4, borderaxespad=0)
    save(fig, "groups.png", "The largest gaps are among registered men who are band members",
         "Per cent difference from the comparison group with the same measured characteristics, by group",
         f"{SAMPLE} Standard errors are in output/group_gaps.csv and are large for the smaller groups. The public file cannot "
         f"say who lives on reserve. The hollow 2011 point is a voluntary survey. {SOURCE}")


def identity():
    t = pd.read_csv(OUTPUT / "identity_cohorts.csv")
    colours = {"First Nations, not registered": AQUA, "Métis, not registered": YELLOW, "Indigenous identity or registered": BLUE,
               "Inuit, not registered": MAGENTA, "Registered": ORANGE, "Comparison group": MUTED}
    fig, ax = plt.subplots(figsize=(10, 5.6))
    fig.subplots_adjust(left=0.075, right=0.72, top=0.82, bottom=0.2)
    ax.axhline(1, color=MUTED, lw=1)
    last = t[t.year == 2021].set_index("group").ratio_to_2006
    nudges = {"Registered": -0.012, "Inuit, not registered": 0.012}
    for group, colour in colours.items():
        one = t[t.group == group]
        ax.plot(one.year, one.ratio_to_2006, color=colour, lw=2, label=group)
        ax.scatter(one.year, one.ratio_to_2006, s=38, color=[("white" if x == 2011 else colour) for x in one.year], edgecolor=colour, linewidth=1.6, zorder=3)
        ax.text(2021.3, last[group] + nudges.get(group, 0), f"{group} ({last[group]:.2f})", color=INK, fontsize=9.5, va="center")
    ax.set_xticks(YEARS)
    ax.set_xlabel("Census year (the same people would be five years older at each)")
    ax.set_ylabel("Count relative to 2006")
    save(fig, "identity.png", "Later censuses count more Indigenous people in the same birth years",
         "People born in Canada, aged 25 to 44 in 2006, weighted count relative to 2006",
         "A group followed through time should shrink a little, as the comparison group does. Growth here comes from changes in "
         "reporting, law and coverage, which these files cannot separate. The hollow 2011 point is a voluntary survey. " + SOURCE)


if __name__ == "__main__":
    FIGURES.mkdir(exist_ok=True)
    gaps()
    decomposition()
    characteristics()
    groups()
    identity()
