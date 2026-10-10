#!/usr/bin/env python3
"""Generate the figures added to the paper at revision.

    python3 analysis/make_figures.py

Writes PDF and PNG files to figures/:
  capability_map    Fig. 1   frequency range and lowest measured impedance of reported systems
  bandwidth_design  Fig. 5   limits of the measurement band
  err_full_sweep    Fig. 12  deviation from the reference at all 72 frequencies
  band_rmse         Fig. 13  RMSE by decade band
  linkk_residuals   Fig. 14  linear Kramers-Kronig residuals of both instruments
  arrhenius         Fig. 16  ohmic and polarisation resistance against 1/T
  nyquist_*         Fig. 11  Nyquist plots of the validation sweeps
  nyquist_temp_*    Fig. 15  Nyquist plots of the temperature series

The plots use the default MATLAB colour order and line style with Times New Roman, the
style of the MATLAB figures of the paper (for example Fig. 7(c)). On a computer without Times
New Roman a metric-compatible serif font is used.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, NullLocator, FormatStrFormatter

from eis import CELLS, BANDS, FIGURES, RAW, load, lin_kk, summary
from temperature import temperature_table, arrhenius_fit

# default MATLAB colour order (R2014b and later)
BLUE, ORANGE, YELLOW, PURPLE, GREEN, CYAN, DARKRED = (
    "#0072BD", "#D95319", "#EDB120", "#7E2F8E", "#77AC30", "#4DBEEE", "#A2142F")
BLACK, GREY, PATCH = "#262626", "#808080", "#E6E6E6"
FE, REF = ORANGE, BLUE          # proposed front-end, EC301 reference

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Liberation Serif", "TeX Gyre Termes", "DejaVu Serif"],
    "mathtext.fontset": "custom", "mathtext.rm": "serif", "mathtext.it": "serif:italic",
    "mathtext.bf": "serif:bold", "mathtext.fallback": "stix",
    "font.size": 9, "axes.labelsize": 9.5, "axes.titlesize": 9.5,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "legend.fontsize": 7.5,
    "axes.prop_cycle": cycler(color=[BLUE, ORANGE, YELLOW, PURPLE, GREEN, CYAN, DARKRED]),
    "axes.edgecolor": BLACK, "axes.linewidth": 0.6, "axes.labelcolor": "black",
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
    "xtick.minor.visible": False, "ytick.minor.visible": False,
    "xtick.major.size": 3.5, "ytick.major.size": 3.5, "xtick.minor.size": 2.0, "ytick.minor.size": 2.0,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.minor.width": 0.5, "ytick.minor.width": 0.5,
    "xtick.color": BLACK, "ytick.color": BLACK,
    "axes.grid": True, "grid.color": BLACK, "grid.alpha": 0.15, "grid.linewidth": 0.5, "grid.linestyle": "-",
    "legend.frameon": True, "legend.fancybox": False, "legend.framealpha": 1.0,
    "legend.edgecolor": BLACK, "legend.borderpad": 0.35, "legend.handlelength": 2.0,
    "patch.linewidth": 0.6,
    "lines.linewidth": 1.0, "lines.markersize": 4.0, "figure.dpi": 150,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    "pdf.fonttype": 42, "ps.fonttype": 42})
NAME = {"Samsung": "Samsung INR18650-35E", "LGM50": "LG INR21700-M50"}


def minor_grid(ax, axis="x"):
    """MATLAB 'grid minor' on a logarithmic axis: dotted minor grid lines."""
    ax.minorticks_on()
    if axis == "x":
        ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.grid(True, which="minor", axis=axis, linestyle=":", alpha=0.25, linewidth=0.5)


def panel_label(ax, text):
    """Sub-figure label below the plot, as in the other figures of the paper. It is added under
    the x-axis label when the figure is saved."""
    ax._panel_label = text


def save(fig, name):
    for ax in fig.axes:
        text = getattr(ax, "_panel_label", None)
        if text:
            xl = ax.get_xlabel()
            ax.set_xlabel(f"{xl}\n{text}" if xl else text, linespacing=1.8 if xl else 1.2)
    fig.tight_layout()
    fig.savefig(FIGURES / f"{name}.pdf", metadata={"CreationDate": None})
    fig.savefig(FIGURES / f"{name}.png", dpi=300)
    plt.close(fig)
    print("  figures/" + name)


def capability_map():
    # name, f_min (Hz), f_max (Hz), lowest measured impedance, validated on commercial cells
    rows = [("Juang 2023", 8e3, 1e4, "1 k$\\Omega$", False),
            ("Jenkins 2019", 60, 2e3, "100 $\\Omega$", False),
            ("Burgos 2022", 1, 1e4, "100 $\\Omega$", False),
            ("Matsubara 2021", 0.1, 1e6, "400 $\\Omega$", False),
            ("Grassini 2015", 1e-3, 1e5, "100 $\\Omega$", False),
            ("Zhang 2024", 0.1, 8e2, "m$\\Omega$ range", True),
            ("Carbone 2023", 0.05, 1e2, "m$\\Omega$ range", True),
            ("Wu 2024", 0.1, 2e3, "m$\\Omega$ range", True),
            ("Yue 2026", 1e-2, 5.62e3, "20 m$\\Omega$", True),
            ("This work", 2e-2, 1e4, "30 m$\\Omega$", True)]
    fig, ax = plt.subplots(figsize=(6.7, 3.6))
    for i, (lab, f0, f1, zmin, cell) in enumerate(rows):
        this = lab == "This work"
        col = ORANGE if this else (BLUE if cell else GREY)
        ax.plot([f0, f1], [i, i], "-", color=col, lw=6 if this else 4,
                solid_capstyle="butt", zorder=4)
        ax.plot([f0, f1], [i, i], "|", color="black", ms=8, mew=1.0, zorder=5)
        ax.text(1.5e6, i, zmin, fontsize=8, va="center", color="black",
                fontweight="bold" if this else "normal")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.tick_params(axis="y", which="both", left=False, right=False)
    ax.set_xscale("log")
    ax.set_xlim(5e-4, 1.2e6)
    ax.set_xlabel("Frequency range of reported measurements (Hz)")
    ax.grid(axis="y", visible=False)
    minor_grid(ax)
    ax.text(1.5e6, len(rows) - 0.45, "Lowest\nimpedance", fontsize=8, va="bottom")
    ax.set_ylim(-0.7, len(rows) + 0.4)
    ax.legend(handles=[Patch(facecolor=ORANGE, edgecolor="none", label="This work"),
                       Patch(facecolor=BLUE, edgecolor="none", label="Tested on commercial lithium-ion cells"),
                       Patch(facecolor=GREY, edgecolor="none", label="Tested on resistive or electrode loads")],
              loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, fontsize=8)
    save(fig, "capability_map")


def bandwidth_design():
    f = np.logspace(-3, 6, 3000)
    r_loop = 15.0
    fig, ax = plt.subplots(1, 2, figsize=(7.1, 2.8))
    a = ax[0]
    a.axvspan(2e-2, 1e4, color=PATCH, zorder=0, lw=0)
    for cs, ls, col in ((0.05, ":", BLUE), (0.53, "--", ORANGE), (3.7, "-", YELLOW)):
        x = 2j * np.pi * f * cs * r_loop
        fl = 1 / (2 * np.pi * cs * r_loop)
        a.semilogx(f, 20 * np.log10(np.abs(x / (1 + x))), ls, color=col, lw=1.3,
                   label=rf"$C_s$ = {cs:g} F, $f_L$ = {1e3 * fl:.3g} mHz")
    a.axhline(-3, color="black", lw=0.6, ls="-.")
    a.set_ylim(-30, 2)
    a.set_xlabel("Frequency (Hz)")
    a.set_ylabel(r"$|I_{\rm cell}|/|I_{\rm cell}|_{f\to\infty}$ (dB)")
    panel_label(a, r"(a) Blocking network, $R_{\rm loop}$ = 15 $\Omega$")
    a.legend(loc="lower right", fontsize=7)
    minor_grid(a)
    a = ax[1]
    a.axvspan(2e-2, 1e4, color=PATCH, zorder=0, lw=0)
    fc = 1e4
    s = 1j * f / fc
    filt = 1 / (s ** 2 + np.sqrt(2) * s + 1)
    stage = 1 / (1 + 1j * f / 5e5)
    a.semilogx(f, 20 * np.log10(np.abs(filt)), "-", color=BLUE, lw=1.3,
               label="second-order sensing filter, $f_c$ = 10 kHz")
    a.semilogx(f, 20 * np.log10(np.abs(stage)), "--", color=ORANGE, lw=1.3,
               label="TL064 stage, gain 2 (500 kHz)")
    a.axhline(-3, color="black", lw=0.6, ls="-.")
    a.set_ylim(-30, 2)
    a.set_xlabel("Frequency (Hz)")
    a.set_ylabel("Normalised gain (dB)")
    panel_label(a, "(b) Sensing filter and drive stage")
    a.legend(loc="lower left", fontsize=7)
    minor_grid(a)
    save(fig, "bandwidth_design")


def err_full_sweep():
    fig, ax = plt.subplots(2, 2, figsize=(7.1, 4.8))
    for k, cell in enumerate(CELLS):
        d = load(cell)
        a = ax[0, k]
        a.axhspan(-1, 1, color=PATCH, zorder=0, lw=0)
        a.axhline(0, color="black", lw=0.6)
        a.semilogx(d.f, d.e_re, "o-", color=BLUE, mfc=BLUE, ms=3.2, label=r"$\varepsilon'$ (real part)")
        a.semilogx(d.f, d.e_im, "s-", color=ORANGE, mfc=ORANGE, ms=3.2, label=r"$\varepsilon''$ (imaginary part)")
        panel_label(a, f"({'ab'[k]}) {NAME[cell]}")
        a.set_ylabel(r"Deviation from EC301 (m$\Omega$)")
        a.set_xlim(0.015, 1.3e4)
        lo, hi = a.get_ylim()
        a.set_ylim(lo, hi + 0.35 * (hi - lo))
        a.legend(loc="upper left", ncol=2)
        minor_grid(a)
        a = ax[1, k]
        a.axhline(0, color="black", lw=0.6)
        a.semilogx(d.f, 100 * (d.dut_mag - d.ref_mag) / d.ref_mag, "d-", color=PURPLE, mfc=PURPLE,
                   ms=3.2, label=r"modulus error (%)")
        a.semilogx(d.f, d.dut_ph - d.ref_ph, "^-", color=GREEN, mfc=GREEN, ms=3.2,
                   label=r"phase error ($^\circ$)")
        panel_label(a, f"({'cd'[k]}) {NAME[cell]}")
        a.set_xlabel("Frequency (Hz)")
        a.set_ylabel("Error (% or $^\\circ$)")
        a.set_xlim(0.015, 1.3e4)
        lo, hi = a.get_ylim()
        a.set_ylim(lo, hi + 0.35 * (hi - lo))
        a.legend(loc="upper left", ncol=2)
        minor_grid(a)
    save(fig, "err_full_sweep")


def band_rmse():
    fig, ax = plt.subplots(1, 2, figsize=(7.1, 2.7), sharey=True)
    labels = ["20 mHz\nto 1 Hz", "1 Hz\nto 100 Hz", "100 Hz\nto 1 kHz", "1 kHz\nto 10 kHz"]
    x = np.arange(len(BANDS))
    w = 0.36
    for k, cell in enumerate(CELLS):
        d = load(cell)
        re, im = [], []
        for _, lo, hi in BANDS:
            m = (d.f >= lo) & (d.f < hi)
            re.append(summary(d.e_re[m])["RMSE"])
            im.append(summary(d.e_im[m])["RMSE"])
        a = ax[k]
        a.bar(x - w / 2, re, w, color=BLUE, label="real part", zorder=3, edgecolor="black", lw=0.5)
        a.bar(x + w / 2, im, w, color=ORANGE, label="imaginary part", zorder=3, edgecolor="black", lw=0.5)
        for xi, v in zip(x - w / 2, re):
            a.text(xi, v + 0.03, f"{v:.2f}", ha="center", fontsize=7)
        for xi, v in zip(x + w / 2, im):
            a.text(xi, v + 0.03, f"{v:.2f}", ha="center", fontsize=7)
        a.set_xticks(x)
        a.set_xticklabels(labels, fontsize=7.5)
        a.tick_params(axis="x", which="both", top=False, bottom=False)
        panel_label(a, f"({'ab'[k]}) {NAME[cell]}")
        a.grid(axis="x", visible=False)
        a.set_ylim(0, 1.65)
        if k == 0:
            a.set_ylabel(r"RMSE from EC301 (m$\Omega$)")
            a.legend(ncol=2, loc="upper left")
    save(fig, "band_rmse")


def linkk_residuals():
    fig, ax = plt.subplots(1, 2, figsize=(7.1, 2.7), sharey=True)
    for k, cell in enumerate(CELLS):
        d = load(cell)
        a = ax[k]
        a.axhline(0, color="black", lw=0.6)
        for re_, im_, col, mk, lab in ((d.dut_re, d.dut_im, FE, "s", "This work"),
                                       (d.ref_re, d.ref_im, REF, "o", "EC301")):
            z = re_.values + 1j * im_.values
            fit, _ = lin_kk(d.f.values, z)
            a.semilogx(d.f, 100 * (z.real - fit.real) / np.abs(z), mk, color=col, mfc=col, ms=3.4,
                       label=f"{lab}, real")
            a.semilogx(d.f, 100 * (z.imag - fit.imag) / np.abs(z), mk, color=col, mfc="none", ms=3.4,
                       mew=0.9, label=f"{lab}, imaginary")
        a.set_xlabel("Frequency (Hz)")
        panel_label(a, f"({'ab'[k]}) {NAME[cell]}")
        a.set_xlim(0.015, 1.3e4)
        minor_grid(a)
        if k == 0:
            a.set_ylabel(r"Residual (% of $|Z|$)")
            a.legend(ncol=2, loc="upper left", fontsize=7)
    save(fig, "linkk_residuals")


def arrhenius():
    t = temperature_table()
    fig, ax = plt.subplots(1, 2, figsize=(7.1, 2.8))
    for cell, col, mk in (("Samsung", BLUE, "o"), ("Panasonic", ORANGE, "s")):
        s = t[t.cell == cell]
        x = 1000 / (s.T_C + 273.15)
        for a, key in ((ax[0], "R_ohm"), (ax[1], "R_pol")):
            ea, r2, fit = arrhenius_fit(s.T_C.values, s[key].values)
            inside = ~s.at_edge.values
            a.semilogy(x[inside], s[key][inside], mk, color=col, mfc="none", mew=1.0, ms=4.5)
            a.semilogy(x[~inside], s[key][~inside], mk, color=col, mfc=col, mew=1.0, ms=4.5)
            xx = np.linspace(x.min(), x.max(), 50)
            a.semilogy(xx, fit(xx), "-", color=col, lw=1.0,
                       label=f"{cell}: $E_a$ = {1000 * ea:.0f} meV ($R^2$ = {r2:.2f})")
    edge = Line2D([], [], ls="none", marker="o", color=GREY, mfc=GREY, ms=4.5,
                  label="sweep ended before the sign change")
    for a, title, lab, ticks, lim in ((ax[0], r"(a) Ohmic intercept $R_\Omega$", r"$R_\Omega$ (m$\Omega$)",
                                       [30, 35, 40, 45, 50, 55, 60, 70], (30, 78)),
                                      (ax[1], r"(b) Polarisation resistance $R_{\rm pol}$",
                                       r"$R_{\rm pol}$ (m$\Omega$)", [5, 10, 20, 50, 100, 200, 500], (4, 900))):
        a.set_ylim(*lim)
        a.set_xlabel(r"$1000/T$ (K$^{-1}$)")
        a.set_ylabel(lab)
        panel_label(a, title)
        a.yaxis.set_major_locator(FixedLocator(ticks))
        a.yaxis.set_minor_locator(NullLocator())
        a.yaxis.set_major_formatter(FormatStrFormatter("%g"))
        a.tick_params(axis="x", which="both", top=False)
        h, l = a.get_legend_handles_labels()
        a.legend(handles=h + [edge], loc="upper left", fontsize=7)
        top = a.secondary_xaxis("top", functions=(lambda v: 1000 / np.maximum(v, 1e-9) - 273.15,
                                                   lambda c: 1000 / (c + 273.15)))
        top.set_xticks([50, 25, 0, -10])
        top.tick_params(direction="in", length=3.5, width=0.6, color=BLACK)
        top.set_xlabel(r"Temperature ($^\circ$C)", fontsize=8.5, labelpad=2)
    save(fig, "arrhenius")


def nyquist_validation():
    """Fig. 11: Nyquist plots of the validation sweeps, one file per cell."""
    lims = {"Samsung": ((42, 66), (-8, 9)), "LGM50": ((29, 44), (-4, 6))}
    for cell, tag in (("Samsung", "samsung"), ("LGM50", "lg")):
        d = load(cell)
        fig, a = plt.subplots(figsize=(3.4, 2.9))
        a.axhline(0, color="black", lw=0.6)
        a.plot(d.dut_re, -d.dut_im, "s-", color=FE, mfc=FE, ms=3.2, lw=1.0,
               label="proposed front-end")
        a.plot(d.ref_re, -d.ref_im, "o-", color=REF, mfc=REF, ms=3.2, lw=1.0,
               label="EC301 potentiostat")
        (x0, x1), (y0, y1) = lims[cell]
        a.set_xlim(x0, x1)
        a.set_ylim(y0, y1)
        a.set_aspect("equal", adjustable="box")
        a.set_xlabel(r"$Z'$ (m$\Omega$)")
        a.set_ylabel(r"$-Z''$ (m$\Omega$)")
        a.legend(loc="upper left", fontsize=7.5)
        hidden = int(((-d.dut_im) < y0).sum())
        print(f"    {cell}: {hidden} front-end points below the plotted range (f >= {d.f[(-d.dut_im) < y0].min():g} Hz)")
        save(fig, f"nyquist_{tag}")


def nyquist_temperature():
    """Fig. 15: Nyquist plots of the temperature series, one file per cell."""
    temps = ["-10", "0", "15", "25", "40", "50"]
    cols = dict(zip(temps, [BLUE, ORANGE, YELLOW, PURPLE, GREEN, CYAN]))
    marks = dict(zip(temps, ["o", "s", "d", "^", "v", ">"]))
    for cell, tag in (("Samsung", "samsung"), ("Panasonic", "panasonic")):
        sheets = pd.read_excel(RAW / f"{cell}.xlsx", sheet_name=None)
        fig, a = plt.subplots(figsize=(3.4, 2.7))
        a.axhline(0, color="black", lw=0.6)
        for t in temps:
            s = sheets[t].sort_values("Frequency")
            a.plot(s.Zreal, s.Zimg, marks[t] + "-", color=cols[t], mfc="none", mew=0.8, ms=3.0,
                   lw=0.8, label=f"${t}$ $^\\circ$C")
        a.set_xlim(25, 200)
        a.set_ylim(-5, 45)
        a.set_aspect("equal", adjustable="box")
        a.set_xlabel(r"$Z'$ (m$\Omega$)")
        a.set_ylabel(r"$-Z''$ (m$\Omega$)")
        a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.42), fontsize=7, ncol=3,
                 handlelength=1.8, columnspacing=1.0)
        save(fig, f"nyquist_temp_{tag}")


if __name__ == "__main__":
    FIGURES.mkdir(exist_ok=True)
    capability_map()
    bandwidth_design()
    err_full_sweep()
    band_rmse()
    linkk_residuals()
    arrhenius()
    nyquist_validation()
    nyquist_temperature()
