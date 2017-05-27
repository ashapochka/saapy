# coding=utf-8
import networkx as nx
import pandas as pd


def file_commit_correlation(file_commit_frame: pd.DataFrame,
                            corr_method='spearman') -> pd.DataFrame:
    return file_commit_frame.corr(method=corr_method)


def build_correlation_graph(correlation: pd.DataFrame,
                            min_corr: float=0.75) -> nx.Graph:
    corr_graph = nx.Graph()
    for column_name in correlation.columns:
        column = correlation[column_name]
        correlated = column[column >= min_corr]
        for row_name, corr in zip(correlated.index, correlated):
            corr_graph.add_edge(column_name, row_name, correlation=corr)
    return corr_graph
