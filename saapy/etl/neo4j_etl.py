# coding=utf-8

import pandas as pd
from toolz import compose
from functools import partial
from typing import List


def neo4j_records_to_dataframe(records):
    if not records:
        df = pd.DataFrame()
    else:
        record_values = (r.values() for r in records)
        df = pd.DataFrame(record_values, columns=records[0].keys())
    return df


def dataframe_to_neo4j_params(dataframe):
    return dataframe.to_dict(orient='records')


def build_neo4j_query(neo4j_client, future_executor=None):
    query = compose(neo4j_records_to_dataframe, neo4j_client.run_query)
    if future_executor:
        return partial(future_executor.submit, query)
    else:
        return query


def build_neo4j_import_nodes(neo4j_client, future_executor=None):
    def import_nodes(dataframe,
                     labels: List[str] = None,
                     chunk_size: int = 1000):
        params = dataframe_to_neo4j_params(dataframe)
        return neo4j_client.import_nodes(params,
                                         labels=labels,
                                         chunk_size=chunk_size)

    if future_executor:
        return partial(future_executor.submit, import_nodes)
    else:
        return import_nodes


def build_neo4j_batch_query(neo4j_client, future_executor=None):
    def batch_query(query, params = None,
                    labels: List[str] = None,
                    chunk_size: int = 1000):
        if isinstance(params, pd.DataFrame):
            query_params = dataframe_to_neo4j_params(params)
        else:
            query_params = params
        return neo4j_client.run_batch_query(query,
                                            labels=labels,
                                            params=query_params,
                                            chunk_size=chunk_size)

    if future_executor:
        return partial(future_executor.submit, batch_query)
    else:
        return batch_query
