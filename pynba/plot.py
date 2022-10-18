"""Module for plotting NBA stuff"""

import json
import os
from pkg_resources import resource_filename

from bokeh.plotting import ColumnDataSource, figure
from bokeh.models import HoverTool
from bokeh.embed import json_item
from bokeh.themes import Theme

from pynba.config import config
from pynba import constants
from pynba.team_info import team_abb_to_id


__all__ = [
    "bokeh_theme",
    "plot_logos",
    "plot_paces",
    "plot_ratings",
    "save_team_plots",
]


def bokeh_theme(name):
    """Load Bokeh theme from themes directory"""
    return Theme(resource_filename("pynba", f"themes/{name}.yaml"))


def _logo_url(team, league, year):
    if league == constants.G_LEAGUE:
        return f"https://stats.gleague.nba.com/media/img/teams/logos/{team}.svg"
    if league == constants.WNBA:
        return f"https://stats.wnba.com/media/img/teams/logos/{team}.svg"
    if league == constants.NBA:
        team_id = team_abb_to_id(league, year)[team]
        return f"https://cdn.nba.com/logos/nba/{team_id}/primary/L/logo.svg"
    raise Exception(f"Invalid league {league} provided")


def plot_logos(data, x_name, y_name, size, fig):
    """Plots NBA logos on a bokeh figure
    Parameters
    ----------
    data : pandas.DataFrame
        must contain team (str), league (str), and year (int) columns
    x_name : str
        column name of dataframe column to be plotted on the x axis
    y_name : str
        column name of dataframe column to be plotted on the y axis
    size : number
        size of images in marker size units.
    fig : bokeh.plotting.figure
        Bokeh figure on which logos are to be plotted
    Returns
    -------
    None
    """
    source = ColumnDataSource(data)
    source.data["logo_url"] = [
        _logo_url(team, league, year)
        for team, league, year in zip(data["team"], data["league"], data["year"])
    ]

    images = fig.image_url(
        url="logo_url",
        x=x_name,
        y=y_name,
        source=source,
        w=size,
        h=size,
        w_units="screen",
        h_units="screen",
        anchor="center",
    )
    circles = fig.circle(x=x_name, y=y_name, size=size, alpha=0, source=source)

    bound = data.loc[:, [x_name, y_name]].abs().max().max()
    fig.circle(x=[bound, -bound], y=[bound, -bound], size=size, alpha=0)

    hover_tool = HoverTool(renderers=[images, circles])
    fig.add_tools(hover_tool)


def plot_ratings(team_stats):
    """Plot team off/def ratings using Bokeh"""
    league = team_stats["league"].iloc[0]
    year = team_stats["year"].iloc[0]
    season_type = team_stats["season_type"].iloc[0]

    fig = figure(
        title=f"{league} {year} {season_type}",
        sizing_mode="scale_both",
        aspect_ratio=1,
        max_width=800,
        max_height=800,
    )

    plot_logos(
        data=team_stats,
        x_name="off_scoring_above_average",
        y_name="def_scoring_above_average",
        size=40,
        fig=fig,
    )

    fig.tools[-1].tooltips = [
        ("Team", "@team"),
        ("Off", "@off_scoring_above_average{0.0}"),
        ("Def", "@def_scoring_above_average{0.0}"),
        ("Tot", "@net_scoring_rate{0.0}"),
    ]

    fig.xaxis.axis_label = "Offensive Rating (pts/100 poss)"
    fig.yaxis.axis_label = "Defensive Rating (pts/100 poss)"

    return fig


def plot_paces(team_stats):
    """Plot team off/def pace using Bokeh"""
    league = team_stats["league"].iloc[0]
    year = team_stats["year"].iloc[0]
    season_type = team_stats["season_type"].iloc[0]

    fig = figure(title=f"{league} {year} {season_type}", width=1000, height=1000)

    plot_logos(
        data=team_stats,
        x_name="off_pace_above_average",
        y_name="def_pace_above_average",
        size=40,
        fig=fig,
    )

    fig.tools[-1].tooltips = [
        ("Team", "@team"),
        ("Off", "@off_pace_above_average{0.0}"),
        ("Def", "@def_pace_above_average{0.0}"),
        ("Tot", "@total_pace{0.0}"),
    ]

    fig.xaxis.axis_label = "Offensive Pace (poss/48 min)"
    fig.yaxis.axis_label = "Defensive Rating (poss/48 min)"

    return fig


def save_team_plots(teams):
    """
    Save Bokeh json files for rendering in the browser
    """
    league = teams["league"].iloc[0]
    year = teams["year"].iloc[0]
    season_type = teams["season_type"].iloc[0]
    theme = bokeh_theme("transparent")

    fig = plot_ratings(teams)
    fig_json = json_item(fig, theme=theme)
    filename = os.path.join(
        config.local_data_directory,
        config.plots_directory,
        f"team_ratings_{league}_{year}_{season_type}.json",
    )
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(fig_json, json_file)

    fig = plot_paces(teams)
    fig_json = json_item(fig, theme=theme)
    filename = os.path.join(
        config.local_data_directory,
        config.plots_directory,
        f"team_paces_{league}_{year}_{season_type}.json",
    )
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(fig_json, json_file)
