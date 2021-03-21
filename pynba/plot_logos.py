import os
from pkg_resources import resource_filename

from PIL import Image as pilimg
import numpy as np


LOGO_DIR_PATH = resource_filename('pynba', 'logos')


def plot_images(xs, ys, image_paths, ax, alpha=None, size=None):
    if alpha is None:
        alpha = 1
    if size is None:
        size = 20

    # plot placeholders and lock in the axis limits
    ax.plot(xs, ys, 'o', mfc='None', mec='None', markersize=size)
    ax.axis(ax.axis())

    for x, y, image_path in zip(xs, ys, image_paths):
        with pilimg.open(image_path) as image:
            offsetsPx = np.array([sz / max(image.size) * size / 72 / 2 *
                                    ax.get_figure().dpi for sz in image.size])
            pxPerUnit = ax.transData.transform((1, 1)) - \
                ax.transData.transform((0, 0))
            offsetsUnit = offsetsPx / pxPerUnit
            extent = (x - offsetsUnit[0], x + offsetsUnit[0],
                        y - offsetsUnit[1], y + offsetsUnit[1])
            ax.imshow(image, alpha=alpha, extent=extent, aspect='auto',
                        interpolation='bilinear')


def plot_logos(xs, ys, teams, ax, alpha=None, size=None):
    image_paths = [os.path.join(LOGO_DIR_PATH, f'{team}.png') for team in teams]
    plot_images(xs, ys, image_paths, ax, alpha=alpha, size=size)
