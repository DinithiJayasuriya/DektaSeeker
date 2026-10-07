#!/usr/bin/env python3
"""Generated converter graph -> netlist triples the bench can simulate.

This is the adapter between the two halves of the converter pipeline. The
diffusion prior emits the ``circuit_base`` one-hot tensors that
``converter_validity.check`` already reads; ``bench.evaluate`` wants
``[(device, netA, netB)]``. Nothing else translated between them.

Intended order of operations:

    X, E  ->  check(node_types, adj)  ->  to_netlist(...)  ->  bench.evaluate(...)

``to_netlist`` assumes the graph already passed ``check``. It re-verifies the
two properties it actually depends on -- devices are two-terminal and edges run
device-to-net -- and raises rather than silently emitting a wrong circuit.
"""
from __future__ import annotations

import numpy as np

# circuit_base class ids, duplicated exactly as converter_validity.py does so
# this module needs neither torch nor graph_tool.
NODE_NMOS, NODE_PMOS = 0, 1
NODE_C, NODE_L = 5, 6
NODE_GND, NODE_VIN, NODE_VOUT, NODE_NET = 10, 13, 14, 15
EDGE_TERM_PLUS = 8

DEVICE_CLASSES = (NODE_NMOS, NODE_PMOS, NODE_C, NODE_L)
NET_CLASSES = (NODE_GND, NODE_VIN, NODE_VOUT, NODE_NET)

# build_lamagic_graphs.py's slot map: Sa -> NMOS slot, Sb -> PMOS slot.
DEVICE_PREFIX = {NODE_NMOS: "Sa", NODE_PMOS: "Sb", NODE_C: "C", NODE_L: "L"}
# bench.py's node vocabulary (LaMAGIC's netlist convention).
RAIL_NAME = {NODE_VIN: "IN", NODE_VOUT: "OUT", NODE_GND: "0"}


class DecodeError(ValueError):
    pass


def from_pyg(data):
    """PyG Data (one-hot x, edge_index, edge_attr) -> (node_types, dense adj).

    Same convention as score_lamagic_validity.py, so a graph decodes exactly as
    the validity gate saw it.
    """
    node_types = data.x.argmax(dim=1).numpy()
    n = len(node_types)
    adj = np.zeros((n, n), dtype=int)
    ei = data.edge_index.numpy()
    ecls = data.edge_attr.argmax(dim=1).numpy()
    adj[ei[0], ei[1]] = ecls
    return node_types, adj


def to_netlist(node_types, adj):
    """-> [(device_name, netA, netB)] for bench.evaluate / bench.build_deck."""
    node_types = np.asarray(node_types).astype(int).reshape(-1)
    adj = np.asarray(adj).astype(int)
    n = len(node_types)
    if adj.shape != (n, n):
        raise DecodeError(f"adj is {adj.shape}, expected ({n}, {n})")

    is_dev = np.isin(node_types, DEVICE_CLASSES)
    is_net = np.isin(node_types, NET_CLASSES)
    if not np.all(is_dev | is_net):
        bad = sorted(set(node_types[~(is_dev | is_net)].tolist()))
        raise DecodeError(f"node classes outside this domain: {bad}")

    # Net names. Rails are named by class; internal nets by index, which keeps
    # them unique and stable under the device ordering below.
    net_name = {}
    for cls, name in RAIL_NAME.items():
        idx = np.flatnonzero(node_types == cls)
        if len(idx) != 1:
            raise DecodeError(f"expected exactly one {name} rail, found {len(idx)}")
        net_name[int(idx[0])] = name
    for j in np.flatnonzero(node_types == NODE_NET):
        net_name[int(j)] = f"n{int(j)}"

    counter = {p: 0 for p in DEVICE_PREFIX.values()}
    out = []
    for i in np.flatnonzero(is_dev):
        i = int(i)
        nbr = [int(j) for j in np.flatnonzero(adj[i] == EDGE_TERM_PLUS) if j != i]
        if len(nbr) != 2:
            raise DecodeError(f"device node {i} has {len(nbr)} terminals, expected 2")
        if not all(is_net[j] for j in nbr):
            raise DecodeError(f"device node {i} is wired to a non-net node")
        if nbr[0] == nbr[1]:
            raise DecodeError(f"device node {i} has both pins on one net")
        prefix = DEVICE_PREFIX[int(node_types[i])]
        name = f"{prefix}{counter[prefix]}"
        counter[prefix] += 1
        out.append((name, net_name[nbr[0]], net_name[nbr[1]]))

    if not out:
        raise DecodeError("no devices")
    if not any(d.startswith("S") for d, _, _ in out):
        raise DecodeError("no switches: not a switched converter")
    return out


def canonical(netlist):
    """Order-independent, net-naming-independent signature of a circuit.

    Used to compare a decoded netlist against the record it came from: internal
    net ids are arbitrary, so equality has to be up to renaming them. Refines a
    colouring of nets by the multiset of (device class, other-end colour)
    incident on them -- Weisfeiler-Lehman on the bipartite graph -- then reports
    the device list in terms of the stable colours.
    """
    nets = sorted({x for _, a, b in netlist for x in (a, b)})
    # rails keep their identity; internal nets all start the same colour
    colour = {x: (x if x in ("IN", "OUT", "0") else "_") for x in nets}
    inc = {x: [] for x in nets}
    for dev, a, b in netlist:
        kind = dev[:2] if dev[0] == "S" else dev[0]
        inc[a].append((kind, b))
        inc[b].append((kind, a))
    for _ in range(len(nets) + 1):
        new = {x: str(sorted((k, colour[y]) for k, y in inc[x])) + "|" + colour[x]
               for x in nets}
        # compress to keep strings bounded
        order = {v: str(i) for i, v in enumerate(sorted(set(new.values())))}
        new = {x: order[v] for x, v in new.items()}
        for x in ("IN", "OUT", "0"):
            if x in new:
                new[x] = x + new[x]
        if new == colour:
            break
        colour = new
    return tuple(sorted(
        (dev[:2] if dev[0] == "S" else dev[0],) + tuple(sorted((colour[a], colour[b])))
        for dev, a, b in netlist))
