#!/usr/bin/env python3
"""Stage 1 (power converters): LaMAGIC circuits -> bipartite PyG graphs.

The analog counterpart is ``build_graphs.py`` (SPICE netlists -> graphs). This
file is the power-converter domain's version: it reads LaMAGIC's already-
bipartite device/net hypergraphs and emits the SAME ``Data`` schema DiGress
consumes, so Stage 2 is the unchanged Hydra entrypoint with
``dataset=lamagic``.

NO MOTIF LAYER. The analog pipeline mines 1-2 device motifs because AnalogGenie
circuits are median 30 devices, so a macro-graph is a real abstraction. LaMAGIC
circuits are 3-6 components -- motif decomposition would produce 3-4 macro nodes
from 5 devices, and the mined vocabulary (MOSFET drain/gate/source pin-role WL
hashes) has no analogue for two-terminal switches anyway. We train directly on
the device-net graph, which is also LaMAGIC's own representation and so keeps
the baseline comparison clean.

Input format (``data/LaMAGIC-dataset/filtered/*_filtered.json``, a list):
  list_of_node : device names ('Sa0','Sb1','L0','C1') + rail names
                 ('VIN','VOUT','GND') + integer net ids
  list_of_edge : unordered {name, net_id} pairs -- EITHER order occurs
  duty_cycle   : one of DUTY_VALUES
  vout, eff    : ngspice labels (NOT used -- see "Conditioning" below)

Node-class slot map (reuses circuit_base's 16-wide one-hot so every downstream
consumer -- extra_features_circuit, dataset_infos, the SDEdit/clamp code in
agents/regen -- works untouched; unused slots simply get zero marginal):
  Sa -> NODE_NMOS   phase-a switch        VIN net -> NODE_VIN
  Sb -> NODE_PMOS   phase-b switch        VOUT net -> NODE_VOUT
  C  -> NODE_C                            GND net -> NODE_GND
  L  -> NODE_L                            internal net -> NODE_NET

Rails are NOT kept as their own nodes: 'VIN' attaches to exactly one net, so we
fold it in and that net carries class NODE_VIN.

Edges: one class only, EDGE_TERM_PLUS, for every device-net incidence. LaMAGIC
switches, inductors and caps are ideal and two-terminal, and LaMAGIC's own
formulation is an unordered hyperedge list -- there is no polarity to learn, so
encoding one would teach the model a spurious asymmetry.

Conditioning (``Data.y``): a DUTY-CYCLE one-hot, nothing else. We deliberately
do NOT condition on vout/eff. Performance-conditioned direct generation IS the
LaMAGIC baseline; SteerGenSE's claim is that the prior supplies the feasible
region while the agents + external simulation do the discovering. Conditioning
on the labels would concede the comparison.

No ``x_size``: LaMAGIC devices carry no free continuous parameters (edge_attr's
Ron / L=10mH are fixed or derived from duty). Omitting the attribute sets
output_dims['X_size']=0, so DiGress's sizing regression head is switched off
rather than trained against a tensor of zeros.

Run:
    python topology_generation/build_lamagic_graphs.py
    python topology_generation/build_lamagic_graphs.py --sources 345comp
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

# graph_tool must come before torch (libgomp ABI).
import graph_tool as _gt  # noqa: F401

_HERE = os.path.dirname(os.path.abspath(__file__))
_DIGRESS_SRC = os.path.normpath(os.path.join(_HERE, "..", "src"))
if _DIGRESS_SRC not in sys.path:
    sys.path.insert(0, _DIGRESS_SRC)

import torch
from torch_geometric.data import Data, InMemoryDataset

from datasets.circuit_base import (
    N_NODE_TYPES, N_EDGE_TYPES,
    NODE_NMOS, NODE_PMOS, NODE_C, NODE_L,
    NODE_GND, NODE_VIN, NODE_VOUT, NODE_NET,
    EDGE_TERM_PLUS,
    DIGRESS_BASE_PATH,
)

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
RAILS = ("VIN", "VOUT", "GND")
RAIL_TO_CLASS = {"VIN": NODE_VIN, "VOUT": NODE_VOUT, "GND": NODE_GND}

# Device-name prefix -> node class. Longest prefix wins ('Sa' before 'S').
DEVICE_PREFIX_TO_CLASS = {"Sa": NODE_NMOS, "Sb": NODE_PMOS, "C": NODE_C, "L": NODE_L}

# Duty cycle is the only conditioning signal. Both LaMAGIC splits use these
# five values (345comp and 6comp alike -- NOTES.md's "0.1..0.9" is the five odd
# tenths, not nine values). Frozen: the index map is baked into any checkpoint.
DUTY_VALUES = (0.1, 0.3, 0.5, 0.7, 0.9)
DUTY_TO_IDX = {d: i for i, d in enumerate(DUTY_VALUES)}
N_DUTY = len(DUTY_VALUES)


def device_class(name: str):
    """Node class for a device name, or None if the prefix is unknown."""
    for pfx in ("Sa", "Sb", "C", "L"):
        if name.startswith(pfx):
            return DEVICE_PREFIX_TO_CLASS[pfx]
    return None


def duty_onehot(duty: float) -> torch.Tensor:
    y = torch.zeros(1, N_DUTY, dtype=torch.float)
    y[0, DUTY_TO_IDX[round(duty, 3)]] = 1.0
    return y


# ---------------------------------------------------------------------------
# Record -> graph
# ---------------------------------------------------------------------------
def incidence(rec: dict):
    """Normalise ``list_of_edge`` into {name: [net_id, ...]} + the net id set.

    Pairs appear in either order -- ``['Sa0', 11]`` and ``[5, 'VOUT']`` are both
    in the corpus -- so orient by type, not position.
    """
    inc = collections.defaultdict(list)
    nets = set()
    for e in rec["list_of_edge"]:
        if len(e) != 2:
            return None, None
        a, b = e
        if isinstance(a, str) and isinstance(b, int):
            name, net = a, b
        elif isinstance(b, str) and isinstance(a, int):
            name, net = b, a
        else:
            return None, None
        inc[name].append(net)
        nets.add(net)
    return inc, nets


def record_to_graph(rec: dict):
    """-> (Data, None) on success, or (None, reason) naming the filter that fired.

    This is g(x) at corpus level: structural well-formedness only. Every kept
    graph is a real two-terminal device-net topology with all three rails
    present and one connected component.
    """
    if round(rec.get("duty_cycle", -1), 3) not in DUTY_TO_IDX:
        return None, "duty"

    inc, nets = incidence(rec)
    if inc is None:
        return None, "edge_form"

    devices, rail_net = [], {}
    for n in rec["list_of_node"]:
        if not isinstance(n, str):
            continue
        if n in RAILS:
            pins = inc.get(n, [])
            if len(pins) != 1:
                return None, "rail_degree"     # missing / multiply-attached rail
            rail_net[n] = pins[0]
        else:
            cls = device_class(n)
            if cls is None:
                return None, "unknown_device"
            pins = inc.get(n, [])
            if len(pins) != 2:
                return None, "device_degree"   # not two-terminal as connected
            if pins[0] == pins[1]:
                return None, "shorted_device"  # both pins on one net
            devices.append((n, cls, pins))

    if len(rail_net) != len(RAILS):
        return None, "rail_missing"
    if len(set(rail_net.values())) != len(RAILS):
        return None, "rail_collision"          # e.g. VIN and GND on one net
    if not devices:
        return None, "no_devices"

    # Devices first, then nets -- same node ordering convention as
    # to_bipartite_pyg, so the dense encoder in agents/regen sees a familiar
    # layout (components before nets).
    net_list = sorted(nets)
    net_to_idx = {n: len(devices) + i for i, n in enumerate(net_list)}
    n_total = len(devices) + len(net_list)

    net_class = {n: NODE_NET for n in net_list}
    for rail, net in rail_net.items():
        net_class[net] = RAIL_TO_CLASS[rail]

    X = torch.zeros(n_total, N_NODE_TYPES, dtype=torch.float)
    for i, (_, cls, _) in enumerate(devices):
        X[i, cls] = 1.0
    for net, idx in net_to_idx.items():
        X[idx, net_class[net]] = 1.0

    src, dst = [], []
    for i, (_, _, pins) in enumerate(devices):
        for net in pins:
            j = net_to_idx[net]
            src += [i, j]
            dst += [j, i]

    # Connectivity over the bipartite graph: a converter in two pieces is not a
    # converter, whatever its labels say.
    adj = collections.defaultdict(list)
    for a, b in zip(src, dst):
        adj[a].append(b)
    seen, stack = {0}, [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    if len(seen) != n_total:
        return None, "disconnected"

    edge_index = torch.tensor([src, dst], dtype=torch.long)
    edge_attr = torch.zeros(len(src), N_EDGE_TYPES, dtype=torch.float)
    edge_attr[:, EDGE_TERM_PLUS] = 1.0

    data = Data(
        x=X,
        edge_index=edge_index,
        edge_attr=edge_attr,
        y=duty_onehot(rec["duty_cycle"]),
        n_nodes=torch.tensor([n_total], dtype=torch.long),
    )
    # NOTE: no ``x_size``. LaMAGIC devices carry no free continuous parameters
    # (edge_attr's Ron / L=10mH are fixed or derived from duty), and omitting
    # the attribute sets output_dims['X_size']=0, which switches DiGress's
    # sizing regression head off entirely instead of training it on zeros.
    return data, None


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------
DEFAULT_LAMAGIC_DIR = "/mnt/ssd1/dinithi/steergense_agent/data/LaMAGIC-dataset/filtered"
SOURCE_FILES = {
    "345comp": "345comp_base_filtered.json",
    "6comp": "6_comp_base_filtered.json",
}


def build_corpus(lamagic_dir: str, sources: list) -> tuple:
    data_list = []
    stats = {"total": 0, "kept": 0, "per_source": {},
             "dropped": collections.Counter(), "duty_counts": collections.Counter(),
             "n_nodes_hist": collections.Counter(), "n_devices_hist": collections.Counter()}
    for src_name in sources:
        path = os.path.join(lamagic_dir, SOURCE_FILES[src_name])
        if not os.path.isfile(path):
            sys.exit(f"[build_lamagic] source not found: {path}\n"
                     f"Run data/LaMAGIC-dataset/filter_labels.py first.")
        print(f"[build_lamagic] reading {path}")
        with open(path) as f:
            records = json.load(f)
        kept = 0
        for rec in records:
            stats["total"] += 1
            data, reason = record_to_graph(rec)
            if data is None:
                stats["dropped"][reason] += 1
                continue
            n_dev = int((data.x[:, [NODE_NMOS, NODE_PMOS, NODE_C, NODE_L]].sum(dim=1) > 0).sum())
            stats["n_nodes_hist"][int(data.n_nodes)] += 1
            stats["n_devices_hist"][n_dev] += 1
            stats["duty_counts"][int(data.y.argmax())] += 1
            data_list.append(data)
            kept += 1
        stats["per_source"][src_name] = {"read": len(records), "kept": kept}
        print(f"[build_lamagic]   {src_name}: {len(records)} -> {kept} graphs")
    stats["kept"] = len(data_list)
    stats["dropped"] = dict(stats["dropped"])
    stats["duty_counts"] = {str(DUTY_VALUES[k]): v for k, v in sorted(stats["duty_counts"].items())}
    stats["n_nodes_hist"] = dict(sorted(stats["n_nodes_hist"].items()))
    stats["n_devices_hist"] = dict(sorted(stats["n_devices_hist"].items()))
    stats["duty_index"] = {str(d): i for d, i in DUTY_TO_IDX.items()}
    return data_list, stats


def split_and_save(data_list, out_dir, train_frac=0.9, val_frac=0.05, seed=0):
    os.makedirs(out_dir, exist_ok=True)
    gen = torch.Generator().manual_seed(seed)
    perm = torch.randperm(len(data_list), generator=gen).tolist()
    n_train = int(train_frac * len(data_list))
    n_val = int(val_frac * len(data_list))
    splits = {"train": perm[:n_train],
              "val": perm[n_train:n_train + n_val],
              "test": perm[n_train + n_val:]}
    sizes = {}
    for name, idx in splits.items():
        collated = InMemoryDataset.collate([data_list[i] for i in idx])
        torch.save(collated, os.path.join(out_dir, f"{name}.pt"))
        sizes[name] = len(idx)
    return sizes


DEFAULT_OUT_DIR = os.path.join(_HERE, "lamagic_graphs")


def main():
    ap = argparse.ArgumentParser(description="Stage 1 (converters): LaMAGIC -> bipartite PyG graphs.")
    ap.add_argument("--lamagic_dir", default=DEFAULT_LAMAGIC_DIR)
    ap.add_argument("--sources", nargs="+", default=["345comp", "6comp"],
                    choices=sorted(SOURCE_FILES))
    ap.add_argument("--out_dir", default=DEFAULT_OUT_DIR)
    ap.add_argument("--train_frac", type=float, default=0.9)
    ap.add_argument("--val_frac", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    data_list, stats = build_corpus(args.lamagic_dir, args.sources)
    print(f"[build_lamagic] {stats['total']} records -> {stats['kept']} graphs")
    print(f"[build_lamagic] dropped: {stats['dropped']}")
    print(f"[build_lamagic] devices/graph: {stats['n_devices_hist']}")
    print(f"[build_lamagic] nodes/graph:   {stats['n_nodes_hist']}")
    print(f"[build_lamagic] duty counts:   {stats['duty_counts']}")

    sizes = split_and_save(data_list, args.out_dir, args.train_frac, args.val_frac, args.seed)
    print(f"[build_lamagic] wrote {args.out_dir}: "
          f"train={sizes['train']} val={sizes['val']} test={sizes['test']}")

    with open(os.path.join(args.out_dir, "stats.json"), "w") as f:
        json.dump(dict(stats=stats, splits=sizes, seed=args.seed,
                       sources=args.sources, n_label_classes=N_DUTY,
                       duty_values=list(DUTY_VALUES)), f, indent=2)


if __name__ == "__main__":
    main()
