"""Module for plotting NBA stuff"""

import os
from pkg_resources import resource_filename

import numpy as np
from bokeh.themes import Theme

from pynba.config import config


__all__ = [
    # "plot_logos",
    # "plot_paces",
    # "plot_ratings",
    # "use_blackontrans_style",
    # "save_team_plots",
    "bokeh_theme"
]


def bokeh_theme(name):
    """Load Bokeh theme from themes directory"""
    return Theme(resource_filename("pynba", f"themes/{name}.yaml"))


# def plot_logos(x_vals, y_vals, teams, league):
#     """Plots NBA logos on a matplotlib axis

#     Parameters
#     ----------
#     x_vals : Iterable of numbers
#         x axis values for plotting.
#     y_vals : Iterable of numbers
#         y axis values for plotting.
#     teams : Iterable of str
#         three letter abbreviations for each team.
#     league : str
#         e.g. "wnba" or "nba"
#     ax : matplotlib axis object
#         axis on which images are plotted.
#     alpha : number
#         transparency of images, 0 being fully transparent.
#     size : number
#         size of images in marker size units.

#     Returns
#     -------
#     None
#     """
#     logo_dir_path = resource_filename("pynba", "logos")
#     image_paths = [
#         os.path.join(logo_dir_path, f"{league}_{team}.png") for team in teams
#     ]
#     plot_images(x_vals, y_vals, image_paths, axis, alpha=alpha, size=size)


# def plot_ratings(team_stats, axis):
#     """Plot team off/def ratings on the provided axis"""
#     league = team_stats["league"].iloc[0]
#     year = team_stats["year"].iloc[0]
#     season_type = team_stats["season_type"].iloc[0]
#     x_vals = team_stats["off_scoring_above_average"]
#     y_vals = team_stats["def_scoring_above_average"]
#     size = 30
#     _center_axis(x_vals, y_vals, axis, size)
#     plot_logos(
#         x_vals,
#         y_vals,
#         team_stats["team"],
#         league,
#         axis,
#         size=size,
#     )
#     axis.set_xlabel("Offensive Rating (pts/poss)")
#     axis.set_ylabel("Defensive Rating (pts/poss)")
#     axis.set_title(f"{league} {year} {season_type}")


# def plot_paces(team_stats, axis):
#     """Plot team off/def pace on the provided axis"""
#     league = team_stats["league"].iloc[0]
#     year = team_stats["year"].iloc[0]
#     season_type = team_stats["season_type"].iloc[0]
#     x_vals = team_stats["off_pace_above_average"]
#     y_vals = team_stats["def_pace_above_average"]
#     size = 30
#     _center_axis(x_vals, y_vals, axis, size)
#     plot_logos(
#         x_vals,
#         y_vals,
#         team_stats["team"],
#         league,
#         axis,
#         size=size,
#     )
#     axis.set_xlabel("Offensive Pace (poss/48)")
#     axis.set_ylabel("Defensive Pace (poss/48)")
#     axis.set_title(f"{league} {year} {season_type}")


# def save_team_plots(teams):
#     """
#     Save some plots from the teams data (to be replaced by D3 interactives)
#     """
#     league = teams["league"].iloc[0]
#     year = teams["year"].iloc[0]
#     season_type = teams["season_type"].iloc[0]

#     fig = plt.figure(figsize=(8, 8))
#     axis = fig.add_subplot(1, 1, 1)
#     plot_ratings(teams, axis)
#     fig.savefig(
#         os.path.join(
#             config.local_data_directory,
#             config.plots_directory,
#             f"team_ratings_{league}_{year}_{season_type}.png",
#         )
#     )

#     fig = plt.figure(figsize=(8, 8))
#     axis = fig.add_subplot(1, 1, 1)
#     plot_paces(teams, axis)
#     fig.savefig(
#         os.path.join(
#             config.local_data_directory,
#             config.plots_directory,
#             f"team_paces_{league}_{year}_{season_type}.png",
#         )
#     )
