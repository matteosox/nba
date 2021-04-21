"""Function providing pbpstats client"""

import os

from pbpstats.client import Client

from pynba.config import config


def pbpstats_client(source, provider):
    """
    Function to provide a pbpstats client with the
    appropriate data directory, and configurable source
    and data provider.
    """
    settings = {
        "dir": os.path.join(config.local_data_directory, config.pbpstats_directory),
        "Boxscore": {"source": source, "data_provider": provider},
        "EnhancedPbp": {"source": source, "data_provider": provider},
        "Games": {"source": source, "data_provider": provider},
        "Pbp": {"source": source, "data_provider": provider},
        "Possessions": {"source": source, "data_provider": provider},
    }
    return Client(settings)
