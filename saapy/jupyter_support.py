def configure_jupyter_environment():
    """
    should be called first to configure environment in the jupyter notebook
    in order to show matplotlib plots correctly, set up logging, import
    matplotlib.pyplot as plt, import numpy as np
    :return:
    """
    import logging
    logging.captureWarnings(True)  # mostly warnings caused by self-signed certs

    # next two liner switchs matplotlib to non-interactive mode
    # to stop osx python rocket launcher from jumping in the dock
    # http://leancrew.com/all-this/2014/01/stopping-the-python-rocketship-icon/
    import matplotlib
    matplotlib.use("Agg") # disable rocket launcher in OSX

    from IPython import get_ipython
    ipython = get_ipython()
    ipython.magic("%pylab notebook") # set up matplotlib and numpy
