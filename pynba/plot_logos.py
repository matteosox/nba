"""Module for plotting images, and specifically NBA logos"""

import os
from pkg_resources import resource_filename

from PIL import Image as pilimg
import numpy as np


LOGO_DIR_PATH = resource_filename("pynba", "logos")


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


def plot_logos(x_vals, y_vals, teams, axis, alpha=None, size=None):
    """Plots NBA logos on a matplotlib axis

    Parameters
    ----------
    x_vals : Iterable of numbers
        x axis values for plotting.
    y_vals : Iterable of numbers
        y axis values for plotting.
    teams : Iterable of str
        three letter abbreviations for each team.
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
    image_paths = [os.path.join(LOGO_DIR_PATH, f"{team}.png") for team in teams]
    plot_images(x_vals, y_vals, image_paths, axis, alpha=alpha, size=size)
