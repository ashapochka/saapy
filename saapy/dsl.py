import networkx as nx
from typing import Iterable


class ModelNode:
    def __init__(self, name, context_model):
        self.name = name
        self._context_model = context_model
        super().__init__()

    def depends_on(self, *nodes, relation=None):
        self._context_model.relate([self], nodes, relation=relation)

    def relates_to(self, *nodes, relation=None):
        self._context_model.relate(nodes, [self], relation=relation)

    def __str__(self):
        return self.name


class Decision(ModelNode):
    def __init__(self, name, context_model):
        super().__init__(name, context_model)


class Uncertainty(ModelNode):
    def __init__(self, name, context_model):
        super().__init__(name, context_model)


class AssessmentModel:
    def __init__(self):
        self._influence_graph = nx.DiGraph()
        super().__init__()

    @property
    def graph(self):
        return self._influence_graph

    def decisions(self, *names):
        return self._nodes(*names, node_type=Decision)

    def uncertainties(self, *names):
        return self._nodes(*names, node_type=Uncertainty)

    def relate(self, source_nodes: list,
               target_nodes: list,
               relation=None) -> None:
        for src in source_nodes:
            for trg in target_nodes:
                self._influence_graph.add_edge(str(src), str(trg), {
                    "relation": relation
                })

    def _nodes(self, *names, node_type=None):
        if len(names) > 1:
            result = [self._node(name, node_type) for name in names]
        elif len(names) == 1:
            result = self._node(names[0], node_type)
        else:
            result = None
        return result

    def _node(self, name, node_type):
        if name in self._influence_graph:
            node_attrs = self._influence_graph[name]
            current_node_object = node_attrs['node_object']
            if not isinstance(current_node_object, node_type):
                error_msg = "Selected node type expected {0) but found {1}"
                raise TypeError(error_msg.format(
                    node_type.__name__, type(current_node_object).__name__))
            node_object = current_node_object
        else:
            new_node_object = node_type(name, self)
            self._influence_graph.add_node(
                name, {'node_object': new_node_object})
            node_object = new_node_object
        return node_object


def model():
    return AssessmentModel()
