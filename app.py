import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import random
import plotly.graph_objects as go
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# ----------------------------------------
# PAGE CONFIG
# ----------------------------------------

st.set_page_config(
    page_title="Quantum Encryption Demo",
    page_icon="🔐",
    layout="wide"
)

# ----------------------------------------
# CUSTOM CSS
# ----------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #050816, #0b1026);
        color: white;
    }

    .title {
        font-size: 60px;
        font-weight: 900;
        text-align: center;
        color: #00F5FF;
        text-shadow: 0px 0px 25px cyan;
    }

    .subtitle {
        text-align: center;
        font-size: 22px;
        color: #B8C1EC;
        margin-bottom: 30px;
    }

    .metric-card {
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 0 15px rgba(0,255,255,0.2);
    }

    .protocol-box {
        background: rgba(0,255,255,0.05);
        border-radius: 15px;
        padding: 15px;
        margin-top: 15px;
        border-left: 4px solid cyan;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------
# TITLE
# ----------------------------------------

st.markdown('<div class="title">🔐 Quantum Encryption Demo</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">BB84 Quantum Key Distribution Visualizer with Eavesdropping Detection</div>',
    unsafe_allow_html=True
)

# ----------------------------------------
# SIDEBAR CONTROLS
# ----------------------------------------

st.sidebar.title("⚙ Simulation Controls")

num_bits = st.sidebar.slider("Number of Qubits", 8, 128, 32)

eavesdrop = st.sidebar.toggle("Enable Eavesdropper (Eve)", value=True)

simulate = st.sidebar.button("🚀 Run Simulation")

# ----------------------------------------
# QUANTUM PROCESSOR STATUS
# ----------------------------------------

st.sidebar.markdown("---")
st.sidebar.subheader("⚛ Quantum Processor")

cpu_load = random.randint(42, 97)
coherence = random.randint(68, 99)

st.sidebar.progress(cpu_load / 100)
st.sidebar.caption(f"Quantum Core Utilization: {cpu_load}%")

st.sidebar.progress(coherence / 100)
st.sidebar.caption(f"Qubit Coherence Stability: {coherence}%")

# ----------------------------------------
# BB84 FUNCTIONS
# ----------------------------------------

def generate_bits(n):
    return np.random.randint(0, 2, n)


def generate_bases(n):
    return np.random.choice(['+', 'x'], n)


def encode_qubits(bits, bases):
    qubits = []

    for bit, base in zip(bits, bases):
        qc = QuantumCircuit(1)

        if bit == 1:
            qc.x(0)

        if base == 'x':
            qc.h(0)

        qubits.append(qc)

    return qubits


def measure_qubits(qubits, bases):
    results = []

    for qc, base in zip(qubits, bases):
        qc_copy = qc.copy()

        if base == 'x':
            qc_copy.h(0)

        state = Statevector.from_instruction(qc_copy)
        probs = state.probabilities()

        result = np.random.choice([0, 1], p=probs)
        results.append(result)

    return np.array(results)


# ----------------------------------------
# RUN SIMULATION
# ----------------------------------------

if simulate:

    alice_bits = generate_bits(num_bits)
    alice_bases = generate_bases(num_bits)

    qubits = encode_qubits(alice_bits, alice_bases)

    # Eve intercepts
    if eavesdrop:
        eve_bases = generate_bases(num_bits)
        eve_results = measure_qubits(qubits, eve_bases)

        qubits = encode_qubits(eve_results, eve_bases)

    bob_bases = generate_bases(num_bits)
    bob_results = measure_qubits(qubits, bob_bases)

    matching = alice_bases == bob_bases

    shared_key_alice = alice_bits[matching]
    shared_key_bob = bob_results[matching]

    errors = np.sum(shared_key_alice != shared_key_bob)

    error_rate = (errors / len(shared_key_alice)) * 100 if len(shared_key_alice) > 0 else 0

    security_status = "⚠ Eavesdropping Detected" if error_rate > 15 else "✅ Secure Channel"

    # ----------------------------------------
    # METRICS
    # ----------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Shared Key Length", len(shared_key_alice))

    with c2:
        st.metric("Errors Detected", errors)

    with c3:
        st.metric("Error Rate", f"{error_rate:.2f}%")

    with c4:
        st.metric("Security Status", security_status)

    # ----------------------------------------
    # QUANTUM STATE VISUALIZATION
    # ----------------------------------------

    st.markdown("## 🌌 Quantum Probability Visualization")

    probabilities = []

    for i in range(min(16, len(qubits))):
        state = Statevector.from_instruction(qubits[i])
        probs = state.probabilities()
        probabilities.append(probs[1])

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=[f"Q{i}" for i in range(len(probabilities))],
            y=probabilities,
            text=[f"{p:.2f}" for p in probabilities],
            textposition='outside'
        )
    )

    fig.update_layout(
        title="Probability of Measuring |1⟩",
        template="plotly_dark",
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=16)
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------
    # QUANTUM NETWORK MAP
    # ----------------------------------------

    st.markdown("## 🌐 Quantum Communication Network")

    G = nx.Graph()

    G.add_node("Alice")
    G.add_node("Quantum Channel")
    G.add_node("Bob")

    if eavesdrop:
        G.add_node("Eve")
        G.add_edge("Alice", "Eve")
        G.add_edge("Eve", "Quantum Channel")
    else:
        G.add_edge("Alice", "Quantum Channel")

    G.add_edge("Quantum Channel", "Bob")

    net = Network(
        height="500px",
        width="100%",
        bgcolor="#050816",
        font_color="white"
    )

    for node in G.nodes:
        net.add_node(node, label=node)

    for edge in G.edges:
        net.add_edge(edge[0], edge[1])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
        net.save_graph(tmpfile.name)

        html_content = open(tmpfile.name, 'r', encoding='utf-8').read()

    components.html(html_content, height=550)

    # ----------------------------------------
    # THREAT LEVEL METER
    # ----------------------------------------

    st.markdown("## 🚨 Quantum Threat Meter")

    threat_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=error_rate,
        title={'text': "Threat Level"},
        gauge={
            'axis': {'range': [0, 30]},
            'bar': {'color': "cyan"},
            'steps': [
                {'range': [0, 10], 'color': '#00ff99'},
                {'range': [10, 20], 'color': '#ffaa00'},
                {'range': [20, 30], 'color': '#ff0055'}
            ]
        }
    ))

    threat_fig.update_layout(
        template="plotly_dark",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(threat_fig, use_container_width=True)

    # ----------------------------------------
    # DATA TABLE
    # ----------------------------------------

    st.markdown("## 📡 Protocol Transmission Data")

    df = pd.DataFrame({
        "Alice Bits": alice_bits,
        "Alice Bases": alice_bases,
        "Bob Bases": bob_bases,
        "Bob Results": bob_results,
        "Basis Match": matching
    })

    st.dataframe(df, use_container_width=True)

    # ----------------------------------------
    # KEY STABILITY VISUALIZATION
    # ----------------------------------------

    st.markdown("## 📈 Shared Key Stability")

    key_match_progress = []
    correct = 0

    for i in range(len(shared_key_alice)):
        if shared_key_alice[i] == shared_key_bob[i]:
            correct += 1

   
