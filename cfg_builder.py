"""
cfg_builder.py  –  Builds and visualises the CFG for authenticate_user.
Usage:
    python cfg_builder.py
Outputs:
    cfg.png   –  control-flow graph image
"""
import ast
import textwrap
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── source ───────────────────────────────────────────────────────────────────
SOURCE = """
def authenticate_user(username, password, db):
    if not username or not password:
        return "Missing credentials"
    if username not in db:
        return "User not found"
    attempts = db[username].get("attempts", 0)
    if attempts >= 3:
        return "Account locked"
    if db[username]["password"] != password:
        db[username]["attempts"] = attempts + 1
        return "Invalid password"
    db[username]["attempts"] = 0
    return "Authenticated"
"""

# ── manual CFG nodes ──────────────────────────────────────────────────────────
nodes = {
    "N1":  "START\nauthenticate_user(username,\npassword, db)",
    "N2":  "if not username\nor not password",
    "N3":  'return\n"Missing credentials"',
    "N4":  "if username\nnot in db",
    "N5":  'return\n"User not found"',
    "N6":  "attempts =\ndb[username].get\n('attempts', 0)",
    "N7":  "if attempts >= 3",
    "N8":  'return\n"Account locked"',
    "N9":  "if db[username]\n['password'] != password",
    "N10": "db[username]['attempts']\n= attempts + 1",
    "N11": 'return\n"Invalid password"',
    "N12": "db[username]['attempts'] = 0",
    "N13": 'return\n"Authenticated"',
}

edges = [
    ("N1",  "N2",  ""),
    ("N2",  "N3",  "True"),
    ("N2",  "N4",  "False"),
    ("N4",  "N5",  "True"),
    ("N4",  "N6",  "False"),
    ("N6",  "N7",  ""),
    ("N7",  "N8",  "True"),
    ("N7",  "N9",  "False"),
    ("N9",  "N10", "True"),
    ("N10", "N11", ""),
    ("N9",  "N12", "False"),
    ("N12", "N13", ""),
]

exit_nodes = {"N3", "N5", "N8", "N11", "N13"}

# ── build graph ───────────────────────────────────────────────────────────────
G = nx.DiGraph()
for n in nodes:
    G.add_node(n, label=nodes[n])
for u, v, lbl in edges:
    G.add_edge(u, v, label=lbl)

# ── layout ────────────────────────────────────────────────────────────────────
pos = {
    "N1":  (3, 12),
    "N2":  (3, 10),
    "N3":  (1, 8.5),
    "N4":  (3, 8.5),
    "N5":  (1, 7),
    "N6":  (3, 7),
    "N7":  (3, 5.5),
    "N8":  (1, 4),
    "N9":  (3, 4),
    "N10": (5, 2.5),
    "N11": (5, 1),
    "N12": (3, 2.5),
    "N13": (3, 1),
}

# ── draw ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 15))
ax.set_facecolor("#F8F9FA")
fig.patch.set_facecolor("#F8F9FA")

decision_nodes = {"N2", "N4", "N7", "N9"}
node_colors = []
for n in G.nodes():
    if n == "N1":
        node_colors.append("#4472C4")
    elif n in exit_nodes:
        node_colors.append("#70AD47")
    elif n in decision_nodes:
        node_colors.append("#ED7D31")
    else:
        node_colors.append("#A9C4E8")

nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                        node_size=3000, node_shape="s", ax=ax, alpha=0.9)
nx.draw_networkx_labels(G, pos,
                         labels={n: nodes[n] for n in G.nodes()},
                         font_size=7, font_color="black", ax=ax)
nx.draw_networkx_edges(G, pos, ax=ax, arrows=True,
                        arrowsize=20, edge_color="#555555",
                        connectionstyle="arc3,rad=0.05", width=1.5)
edge_labels = {(u, v): lbl for u, v, lbl in edges if lbl}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                              font_size=8, font_color="#CC0000", ax=ax)

# legend
patches = [
    mpatches.Patch(color="#4472C4", label="Start"),
    mpatches.Patch(color="#ED7D31", label="Decision (branch)"),
    mpatches.Patch(color="#A9C4E8", label="Statement"),
    mpatches.Patch(color="#70AD47", label="Return (exit)"),
]
ax.legend(handles=patches, loc="lower right", fontsize=9)
ax.set_title("CFG: authenticate_user  |  Cyclomatic Complexity M = 5",
             fontsize=13, fontweight="bold", pad=15)
ax.axis("off")
plt.tight_layout()
plt.savefig("cfg.png", dpi=150, bbox_inches="tight")
print("Saved cfg.png")

# ── cyclomatic complexity ─────────────────────────────────────────────────────
E = G.number_of_edges()
N = G.number_of_nodes()
P = 1  # connected components
M = E - N + 2 * P
print(f"Edges={E}, Nodes={N}, M = {E} - {N} + 2*{P} = {M}")

# ── all simple paths ──────────────────────────────────────────────────────────
print("\nAll execution paths:")
for exit_n in sorted(exit_nodes):
    for path in nx.all_simple_paths(G, source="N1", target=exit_n):
        print("  →".join(path))
