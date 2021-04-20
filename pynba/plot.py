"""Module for plotting NBA stuff"""

import os
from pkg_resources import resource_filename

from PIL import Image as pilimg
import numpy as np
from matplotlib import pyplot as plt

from pynba.config import config


__all__ = [
    "plot_logos",
    "plot_paces",
    "plot_ratings",
    "use_blackontrans_style",
    "save_team_plots",
]


def use_blackontrans_style():
    """Use blackontrans matplotlib style"""
    plt.style.use(resource_filename("pynba", "blackontrans.mplstyle"))


def plot_images(x_vals, y_vals, image_paths, axis, alpha=None, size=None):
    """Plots images on a matplotlib axis

    Parameters
    ----------
    x_vals : Iterable of numbers
        x axis values for plotting.
    y_vals : Iterable of numbers
        y axis values for plotting.
    image_paths : Iterable of str
        file-system paths of images to plot.
    ax : matplotlib axis object
        axis on which images are plotted.
    alpha : number
        transparency of images, 0 being fully transparent.
    size : number
        size of images in marker size units.


    Returns
    -------
    None
    """
    if alpha is None:
        alpha = 1
    if size is None:
        size = 20

    # plot placeholders and lock in the axis limits
    axis.plot(x_vals, y_vals, "o", mfc="None", mec="None", markersize=size)
    axis.axis(axis.axis())

    for x_val, y_val, image_path in zip(x_vals, y_vals, image_paths):
        with pilimg.open(image_path) as image:
            offsets_px = np.array(
                [
                    sz / max(image.size) * size / 72 / 2 * axis.get_figure().dpi
                    for sz in image.size
                ]
            )
            px_per_unit = axis.transData.transform((1, 1)) - axis.transData.transform(
                (0, 0)
            )
            offsets_unit = offsets_px / px_per_unit
            extent = (
                x_val - offsets_unit[0],
                x_val + offsets_unit[0],
                y_val - offsets_unit[1],
                y_val + offsets_unit[1],
            )
            axis.imshow(
                image,
                alpha=alpha,
                extent=extent,
                aspect="auto",
                interpolation="bilinear",
            )


def plot_logos(x_vals, y_vals, teams, league, axis, alpha=None, size=None):
    """Plots NBA logos on a matplotlib axis

    Parameters
    ----------
    x_vals : Iterable of numbers
        x axis values for plotting.
    y_vals : Iterable of numbers
        y axis values for plotting.
    teams : Iterable of str
        three letter abbreviations for each team.
    league : str
        e.g. "wnba" or "nba"
    ax : matplotlib axis object
        axis on which images are plotted.
    alpha : number
        transparency of images, 0 being fully transparent.
    size : number
        size of images in marker size units.

    Returns
    -------
    None
    """
    logo_dir_path = resource_filename("pynba", "logos")
    image_paths = [
        os.path.join(logo_dir_path, f"{league}_{team}.png") for team in teams
    ]
    plot_images(x_vals, y_vals, image_paths, axis, alpha=alpha, size=size)


def plot_ratings(team_stats, axis):
    """Plot team off/def ratings on the provided axis"""
    league = team_stats["league"].iloc[0]
    year = team_stats["year"].iloc[0]
    season_type = team_stats["season_type"].iloc[0]
    x_vals = team_stats["off_scoring_above_average"]
    y_vals = team_stats["def_scoring_above_average"]
    size = 30
    _center_axis(x_vals, y_vals, axis, size)
    plot_logos(
        x_vals,
        y_vals,
        team_stats["team"],
        league,
        axis,
        size=size,
    )
    axis.set_xlabel("Offensive Rating (pts/poss)")
    axis.set_ylabel("Defensive Rating (pts/poss)")
    axis.set_title(f"{league} {year} {season_type}")


def plot_paces(team_stats, axis):
    """Plot team off/def pace on the provided axis"""
    league = team_stats["league"].iloc[0]
    year = team_stats["year"].iloc[0]
    season_type = team_stats["season_type"].iloc[0]
    x_vals = team_stats["off_pace_above_average"]
    y_vals = team_stats["def_pace_above_average"]
    size = 30
    _center_axis(x_vals, y_vals, axis, size)
    plot_logos(
        x_vals,
        y_vals,
        team_stats["team"],
        league,
        axis,
        size=size,
    )
    axis.set_xlabel("Offensive Pace (poss/48)")
    axis.set_ylabel("Defensive Pace (poss/48)")
    axis.set_title(f"{league} {year} {season_type}")


def _center_axis(x_vals, y_vals, axis, size=None):
    axis.plot(
        np.hstack([x_vals, x_vals, -x_vals, -x_vals, y_vals, -y_vals, y_vals, -y_vals]),
        np.hstack([y_vals, -y_vals, y_vals, -y_vals, x_vals, x_vals, -x_vals, -x_vals]),
        "o",
        mfc="None",
        mec="None",
        markersize=size,
    )
    axis.axis(axis.axis("equal"))


def save_team_plots(teams):
    """
    Save some plots from the teams data (to be replaced by D3 interactives)
    """
    league = teams["league"].iloc[0]
    year = teams["year"].iloc[0]
    season_type = teams["season_type"].iloc[0]

    plots_path = os.path.join(config.local_data_directory, config.plots_directory)
    os.makedirs(plots_path, exist_ok=True)

    fig = plt.figure(figsize=(8, 8))
    axis = fig.add_subplot(1, 1, 1)
    plot_ratings(teams, axis)
    fig.savefig(
        os.path.join(
            config.local_data_directory,
            config.plots_directory,
            f"team_ratings_{league}_{year}_{season_type}.png",
        )
    )

    fig = plt.figure(figsize=(8, 8))
    axis = fig.add_subplot(1, 1, 1)
    plot_paces(teams, axis)
    fig.savefig(
        os.path.join(
            config.local_data_directory,
            config.plots_directory,
            f"team_paces_{league}_{year}_{season_type}.png",
        )
    )
