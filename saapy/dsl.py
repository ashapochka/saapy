import networkx as nx
from typing import Iterable


class ModelNode:
    def __init__(self, context_model):
        self._context_model = context_model
        super().__init__()

    def depends_on(self, *nodes, relation=None):
        self._context_model.relate([self], nodes, relation=relation)

    def relates_to(self, *nodes, relation=None):
        self._context_model.relate(nodes, [self], relation=relation)


class Decision(ModelNode):
    def __init__(self, context_model):
        super().__init__(context_model)


class Uncertainty(ModelNode):
    def __init__(self, context_model):
        super().__init__(context_model)


class AssessmentModel:
    def __init__(self):
        self._influence_graph = nx.DiGraph()
        super().__init__()

    def decisions(self, *names) -> Iterable[Decision]:
        return [self._node(name, Decision) for name in names]

    def uncertainties(self, *names):
        return [self._node(name, Uncertainty) for name in names]

    def relate(self, source_nodes: list,
               target_nodes: list,
               relation=None) -> None:
        pass

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
            new_node_object = node_type()
            self._influence_graph.add_node(
                name, {'node_object': new_node_object})
            node_object = new_node_object
        return node_object


def model():
    return AssessmentModel()
