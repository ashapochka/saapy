# coding=utf-8
import matplotlib.pyplot as plt


def plot_ecdf(x, y, xlabel='attribute', legend='x'):
    """
    Plot distribution ECDF
    x should be sorted, y typically from 1/len(x) to 1

    TODO: function should be improved to plot multiple overlayed ecdfs
    """
    plt.plot(x, y, marker='.', linestyle='none')

    # Make nice margins
    plt.margins(0.02)

    # Annotate the plot
    plt.legend((legend,), loc='lower right')
    _ = plt.xlabel(xlabel)
    _ = plt.ylabel('ECDF')

    # Display the plot
    plt.show()
