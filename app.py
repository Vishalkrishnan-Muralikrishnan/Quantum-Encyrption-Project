import streamlit as st
import numpy as np
import pandas as pd
import random
import plotly.graph_objects as go
import streamlit.components.v1 as components
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import networkx as nx
from pyvis.network import Network
import tempfile

# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="Quantum Encryption Lab",
    page_icon="🔐",
    layout="wide"
)

# ----------------------------
# GLOBAL CSS (fix overflow + clean UI)
# ----------------------------

st.markdown(
"""
<style>
.stApp {
    background: linear-gradient(135deg, #050816, #0b1026, #0f172a);
    color: white;
    overflow-x: hidden;
}

.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1200px;
}

h1, h2, h3 {
    color: #22d3ee;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
}

.small {
    font-size: 0.95rem;
    color: #cbd5e1;
}
</style>
""",
unsafe_allow_html=True
)

# ----------------------------
# HEADER
# ----------------------------

st.title("🔐 Quantum Encryption Lab")
st.caption("BB84 Quantum Key Distribution Simulator — with Real-World Cybersecurity Simulation")

# ----------------------------
# INTRO
# ----------------------------

with st.expander("📘 What is this project?"):
    st.write("""
    This simulator demonstrates how quantum encryption (BB84 protocol) protects communication.

    It simulates:
    - Alice sending quantum bits
    - Bob receiving them
    - Optional attacker (Eve)
    - Detection of interception via quantum disturbance

    ⚠ Real-world analogy: Banking transactions (SWIFT system) or secure military communication.
    """)

# ----------------------------
# USER INPUTS (NO SIDEBAR)
# ----------------------------

st.markdown("## ⚙ Simulation Controls")

col1, col2, col3 = st.columns(3)

with col1:
    num_bits = st.slider("Number of Qubits", 8, 128, 32)

with col2:
    mode = st.radio("Mode", ["Secure Channel", "Banking Attack Simulation (Eve Intercepts)"])

with col3:
    run = st.button("🚀 Run Simulation")

# ----------------------------
# REAL-WORLD CONTEXT BOX
# ----------------------------

st.markdown("## 🌍 Real-World Scenario")

st.info("""
Imagine a global bank sending encrypted transaction keys between branches.

If a hacker intercepts classical encryption → data is copied silently.

If quantum encryption is used → interception is detected immediately due to state disturbance.
""")

# ----------------------------
# QUANTUM FUNCTIONS
# ----------------------------

def bits(n):
    return np.random.randint(0, 2, n)

def bases(n):
    return np.random.choice(['+', 'x'], n)

def encode(bits_arr, base_arr):
    q = []
    for b, base in zip(bits_arr, base_arr):
        qc = QuantumCircuit(1)
        if b == 1:
            qc.x(0)
        if base == 'x':
            qc.h(0)
        q.append(qc)
    return q

def measure(qc_list, base_arr):
    res = []
    for qc, base in zip(qc_list, base_arr):
        temp = qc.copy()
        if base == 'x':
            temp.h(0)
        state = Statevector.from_instruction(temp)
        probs = state.probabilities()
        res.append(np.random.choice([0,1], p=probs))
    return np.array(res)

# ----------------------------
# RUN SIMULATION
# ----------------------------

if run:

    eve = (mode != "Secure Channel")

    alice_b = bits(num_bits)
    alice_base = bases(num_bits)

    qubits = encode(alice_b, alice_base)

    if eve:
        eve_base = bases(num_bits)
        eve_res = measure(qubits, eve_base)
        qubits = encode(eve_res, eve_base)

    bob_base = bases(num_bits)
    bob_res = measure(qubits, bob_base)

    match = alice_base == bob_base

    alice_key = alice_b[match]
    bob_key = bob_res[match]

    errors = np.sum(alice_key != bob_key)

    error_rate = (errors / len(alice_key)) * 100 if len(alice_key) else 0

    secure = error_rate < 15

    # ----------------------------
    # RESULT BANNER
    # ----------------------------

    if secure:
        st.success("✔ Secure Quantum Channel Established")
    else:
        st.error("⚠ Attack Detected: Quantum State Disturbance Found")

    # ----------------------------
    # METRICS
    # ----------------------------

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Key Length", len(alice_key))
    m2.metric("Errors", int(errors))
    m3.metric("Error Rate", f"{error_rate:.2f}%")
    m4.metric("Security", "SAFE" if secure else "BREACHED")

    # ----------------------------
    # REAL-WORLD RISK ANALYSIS (IMPROVED)
    # ----------------------------

    st.markdown("## 🏦 Banking Security Risk Analysis")

    if eve:
        st.warning("""
        A cyber attacker intercepted quantum-encrypted banking keys.

        ✔ System response:
        - Interception detected
        - Transaction halted automatically
        - Key regenerated

        💡 In classical systems, this attack would go unnoticed.
        """)
    else:
        st.success("""
        No intrusion detected.
        Banking transactions remain fully secure.
        """)

    # ----------------------------
    # PROBABILITY VISUAL
    # ----------------------------

    st.markdown("## 📊 Quantum State Behavior")

    probs = []
    for i in range(min(16, len(qubits))):
        state = Statevector.from_instruction(qubits[i])
        probs.append(state.probabilities()[1])

    fig = go.Figure()
    fig.add_trace(go.Bar(y=probs, x=[f"Q{i}" for i in range(len(probs))]))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # NETWORK VISUAL (FIXED WIDTH OVERFLOW)
    # ----------------------------

    st.markdown("## 🌐 Quantum Network Flow")

    G = nx.Graph()
    G.add_edges_from([
        ("Bank A", "Quantum Channel"),
        ("Quantum Channel", "Bank B")
    ])

    if eve:
        G.add_node("Hacker")
        G.add_edge("Bank A", "Hacker")
        G.add_edge("Hacker", "Quantum Channel")

    net = Network(height="400px", width="100%", bgcolor="#0b1026", font_color="white")

    for n in G.nodes:
        net.add_node(n)
    for e in G.edges:
        net.add_edge(e[0], e[1])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
        net.save_graph(f.name)
        html = open(f.name).read()

    components.html(html, height=420)

    # ----------------------------
    # FINAL KEY
    # ----------------------------

    st.markdown("## 🔑 Final Shared Key")
    st.code("".join(map(str, alice_key.tolist())))

else:

    st.markdown("""
    ## 👈 How to use

    1. Select number of qubits
    2. Choose simulation mode
    3. Click Run Simulation

    This will simulate secure vs attacked quantum communication in a banking system.
    """)
