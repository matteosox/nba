"""Module for plotting NBA stuff"""

import json
import os
from pkg_resources import resource_filename

from bokeh.plotting import ColumnDataSource, figure
from bokeh.models import Select, HoverTool, CustomJS
from bokeh.embed import json_item
from bokeh.themes import Theme
from bokeh.layouts import column, row

from pynba.config import config


__all__ = [
    "bokeh_theme",
    "save_stats_plot",
]
DEFAULT_X_NAME = "Off Scoring (pts/100 poss)"
DEFAULT_Y_NAME = "Def Scoring (pts/100 poss)"
SIZE = 40
NAMES = {
    "Net Scoring (pts/100 poss)": "net_scoring_rate",
    "Off Scoring (pts/100 poss)": "off_scoring_above_average",
    "Def Scoring (pts/100 poss)": "def_scoring_above_average",
    "Net Pace (poss/48 min)": "total_pace",
    "Off Pace (poss/48 min)": "off_pace",
    "Def Pace (poss/48 min)": "def_pace",
    "Off 3pt Fq": "off_three_attempt_rate",
    "Off 2pt%": "off_two_make_rate",
    "Off 3pt%": "off_three_make_rate",
    "Off Reb%": "off_reb_rate",
    "Off Tov%": "off_turnover_rate",
    "Off FT Fq": "off_ft_attempt_rate",
    "Off FT%": "off_ft_make_rate",
    "Def 3pt Fq": "def_three_attempt_rate",
    "Def 2pt%": "def_two_make_rate",
    "Def 3pt%": "def_three_make_rate",
    "Def Reb%": "def_reb_rate",
    "Def Tov%": "def_turnover_rate",
    "Def FT Fq": "def_ft_attempt_rate",
}


def bokeh_theme(name):
    """Load Bokeh theme from themes directory"""
    return Theme(resource_filename("pynba", f"themes/{name}.yaml"))


def plot_stats(team_stats):
    """Plot team stats using Bokeh"""
    fig = figure(
        sizing_mode="scale_both",
        aspect_ratio=1,
        max_width=800,
        max_height=800,
        tools="",
        toolbar_location=None,
    )

    full_source = ColumnDataSource(team_stats)
    source = ColumnDataSource(
        {
            "x": team_stats[NAMES[DEFAULT_X_NAME]],
            "y": team_stats[NAMES[DEFAULT_Y_NAME]],
            "logo_url": [
                f"/logos/{league}/{team}.svg"
                for team, league in zip(team_stats["team"], team_stats["league"])
            ],
            "team": team_stats["team"],
        }
    )

    images = fig.image_url(
        url="logo_url",
        source=source,
        w=SIZE,
        h=SIZE,
        w_units="screen",
        h_units="screen",
        anchor="center",
    )
    circles = fig.circle(size=SIZE, alpha=0, source=source)

    hover_tool = HoverTool(
        renderers=[images, circles],
        tooltips=[("", "@team"), ("x", "@x{0.1}"), ("y", "@y{0.1}")],
    )
    fig.add_tools(hover_tool)

    fig.xaxis.axis_label = DEFAULT_X_NAME
    fig.yaxis.axis_label = DEFAULT_Y_NAME

    code = """
    axis[0].axis_label = cb_obj.value
    source.data.{} = full_source.data[names[cb_obj.value]]
    source.change.emit()
    """

    callback_x = CustomJS(
        args=dict(source=source, full_source=full_source, names=NAMES, axis=fig.xaxis),
        code=code.format("x"),
    )
    callback_y = CustomJS(
        args=dict(source=source, full_source=full_source, names=NAMES, axis=fig.yaxis),
        code=code.format("y"),
    )

    select_x = Select(
        title="X variable", value=DEFAULT_X_NAME, options=list(NAMES.keys())
    )
    select_x.js_on_change("value", callback_x)
    select_y = Select(
        title="Y variable", value=DEFAULT_Y_NAME, options=list(NAMES.keys())
    )
    select_y.js_on_change("value", callback_y)

    return column(row(select_x, select_y), fig)


def save_stats_plot(teams):
    """Save Bokeh json file for rendering in the browser"""
    league = teams["league"].iloc[0]
    year = teams["year"].iloc[0]
    season_type = teams["season_type"].iloc[0]
    theme = bokeh_theme("transparent")

    col = plot_stats(teams)
    fig_json = json_item(col, theme=theme)
    filename = os.path.join(
        config.local_data_directory,
        config.plots_directory,
        f"team_stats_{league}_{year}_{season_type}.json",
    )
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(fig_json, json_file)
