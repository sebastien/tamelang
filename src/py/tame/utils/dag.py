from typing import Generic, TypeVar, Iterable, Optional, Union
from weakref import WeakValueDictionary

K = TypeVar("K")
T = TypeVar("T")


# NOTE: This is from https://github.com/sebastien/cells/blob/main/src/py/cells/dag.py


class DAGNodeList(Generic[T]):
    def __init__(self):
        self.nodes: list[DAGNodeAdapter[T]] = []

    def append(self, node: "DAGNodeAdapter[T]"):
        assert not self.nodes or node.graph.dag is self.nodes[0].graph.dag
        self.nodes.append(node)
        return self

    def __and__(self, other: "DAGNodeAdapter"):
        # TODO List support
        for node in self.nodes:
            node & other
        return other

    def __or__(self, other: "DAGNodeAdapter[T]") -> "DAGNodeList[T]":
        # TODO List support
        self.nodes.append(other)
        return self


class DAGNodeAdapter(Generic[T]):
    def __init__(self, graph: "DAGGraphAdapter", name: str):
        self.graph = graph
        self.name = name

    @property
    def inputs(self) -> list["DAGNodeAdapter[T]"]:
        return [self.graph.node(_) for _ in self.graph.dag.inputs.get(self.name, [])]

    @property
    def outputs(self) -> list["DAGNodeAdapter[T]"]:
        return [self.graph.node(_) for _ in self.graph.dag.outputs.get(self.name, [])]

    def __and__(self, other: Union["DAGNodeAdapter[T]", DAGNodeList[T]]):
        if isinstance(other, DAGNodeList):
            for node in other.nodes:
                self & node
            return other
        else:
            assert self.graph is other.graph
            self.graph.dag.addInput(other.name, self.name)
            return other

    def __or__(self, other: "DAGNodeAdapter[T]") -> DAGNodeList[T]:
        # TODO List support
        l = DAGNodeList()
        l.append(self)
        l.append(other)
        return l


class DAGGraphAdapter(Generic[T]):
    def __init__(self, dag: Optional["DAG"] = None):
        self.dag = DAG() if dag is None else dag
        self.nodes: dict[str, DAGNodeAdapter] = {}

    @property
    def count(self) -> int:
        return len(self.dag.nodes)

    @property
    def traversal(self) -> Iterable[DAGNodeAdapter]:
        return (self.node(_) for _ in self.dag.ranks())

    def node(self, name: str, value: Optional[T] = None) -> DAGNodeAdapter:
        if name not in self.nodes:
            self.nodes[name] = DAGNodeAdapter(self, name)
            self.dag.setNode(name, value)
        return self.nodes[name]

    def __str__(self) -> str:
        return toASCII(self.dag)


class DAG(Generic[K, T]):
    """A simple data structure to defined a directed acyclic graph that can
    be traversed back and forth."""

    def __init__(self):
        self.nodes: dict[K, Optional[T]] = {}
        self.outputs: dict[K, list[K]] = {}
        self.inputs: dict[K, list[K]] = {}

    def reset(self):
        self.nodes = {}
        self.outputs = {}
        self.inputs = {}
        return self

    def asdict(self):
        return {
            "nodes": self.nodes,
            "edges": self.outputs,
        }

    def getNode(self, node: K) -> Optional[T]:
        return self.nodes.get(node)

    def setNode(self, node: K, value: Optional[T] = None):
        """Associates a value to the node of the given name. Use this to map
        values to the DAG"""
        if node not in self.nodes:
            self.nodes[node] = value
            self.inputs[node] = []
            self.outputs[node] = []
        if value != None:
            self.nodes[node] = value
        return self

    def clearInputs(self, node: K):
        for n in self.inputs.get(node, ()):
            self.outputs[n].remove(node)
        self.inputs[node] = []
        return node

    def setInputs(self, node: K, inputs: list[K]):
        self.clearInputs(node)
        self.addInputs(node, inputs)
        return self

    def addInput(self, node: K, inputNode: K):
        """Add the given node as input to this node"""
        self.setNode(node)
        if inputNode not in self.nodes:
            self.setNode(inputNode)
        assert node in self.inputs, "Output node should have been registered before"
        assert (
            inputNode in self.outputs
        ), "Input node should have been registered before"
        self.inputs[node].append(inputNode)
        self.outputs[inputNode].append(node)
        # TODO: Detect cycle
        return self

    def addInputs(self, node: K, inputNodes: Iterable[K]):
        """Add the given node as inputs to this node"""
        for _ in inputNodes:
            self.addInput(node, _)
        return self

    def addOutput(self, node: K, outputNode: K):
        """Add the given node as outputs of this node"""
        return self.addInput(outputNode, node)

    def addOutputs(self, node: K, outputNode: Iterable[K]):
        """Add the given nodes as outputs of this node"""
        for _ in outputNode:
            self.addOutput(node, _)
        return self

    def ancestors(self, node: K, visited: Optional[list[K]] = None) -> Iterable[K]:
        """Iterates through the precursors/ancestors of the given node"""
        parents = self.inputs.get(node, ())
        v = visited or []
        # NOTE: If there is a cycle, we're fucked!
        for _ in parents:
            yield _
        v += parents
        for _ in parents:
            for n in self.ancestors(_, v):
                if n not in v:
                    v.append(n)
                    yield n

    def descendants(self, node: K) -> Iterable[K]:
        """Iterates through the descendants of the given node"""
        children = self.outputs.get(node, ())
        # NOTE: If there is a cycle, we're fucked!
        for _ in children:
            yield _
        for _ in children:
            yield from self.descendants(_)

    def ranks(self) -> dict[K, int]:
        """Returns the rank for each node in the graph, as a mapping between the
        node id and the rank. Base rank is 0, result is sorted by ascending rank."""
        ranks: dict[K, int] = dict((k, 0) for k in self.nodes)
        while True:
            has_changed = False
            for node in self.nodes:
                rank = (
                    max(ranks[_] for _ in self.inputs[node]) + 1
                    if self.inputs[node]
                    else 0
                )
                has_changed = has_changed or rank != ranks[node]
                ranks[node] = rank
            if not has_changed:
                break
        return {k: v for k, v in sorted(ranks.items(), key=lambda _: _[1])}

    def successors(self, ranks: Optional[dict[K, int]] = None) -> dict[K, list[K]]:
        # NOTE: This may return a N * N-1 matrix, with N the number of nodes,
        # so this might take up a bit of memory on large graphs.
        node_ranks = self.ranks() if ranks is None else ranks
        return {
            node: sorted(self.descendants(node), key=lambda _: node_ranks[_])
            for node in node_ranks
        }


def toASCIILines(dag: DAG) -> Iterable[str]:
    pass


def toASCII(dag: DAG) -> str:
    # return "\n".join(toASCIILines(dag))
    ranks = dag.ranks()
    successors = dag.successors(ranks)
    width = max(len(_) for _ in successors.values())
    depth = max(_ for _ in ranks.values())
    length = max(len(_) for _ in ranks) + 3
    step = " " * length
    tmpl = "{0:" + str(length) + "s}"
    names = {k: tmpl.format(k) for k in ranks}
    res = []

    def arrow(n: int):
        res = ["─"] * n
        res[-1] = " "
        res[-2] = "▶"
        return "".join(res)

    def root(n: int, name: str):
        res = [" " * length * n]
        res.append(name)
        res.append("─" * (length - len(name) - 3))
        res.append("─┐")
        return "".join(res)

    def stem(n: int, isLast: bool):
        res = [" "] * n
        res[-1] = "─"
        res[-2] = "└" if isLast else "├"
        return "".join(res)

    previous_rank = 0
    for node, succ in successors.items():
        rank = ranks[node]
        if rank == depth:
            break
        if rank != previous_rank:
            res.append("")
            previous_rank = rank
        res.append(root(rank, node))
        prefix = " " * (length * (ranks[node] + 1))
        # TODO: We should probably only do the outputs
        for i, other in enumerate(succ):
            src = stem(len(prefix), i == len(succ) - 1)
            dst = f"{arrow(length * ranks[other])}{names[other]}"[len(src) :]
            res.append(f"{src}{dst}")
    return "\n".join(res)


def graph(dag: Optional[DAG] = None) -> DAGGraphAdapter:
    return DAGGraphAdapter(dag)


# EOF
