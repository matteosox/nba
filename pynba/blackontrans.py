"""Set Matplotlib style to black on transparent"""

from matplotlib import pyplot as plt
from pkg_resources import resource_filename


plt.style.use(resource_filename("pynba", "blackontrans.mplstyle"))
