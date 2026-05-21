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

# ------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------

st.set_page_config(
    page_title="Quantum Encryption Lab",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------
# CUSTOM STYLING
# ------------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(135deg,#020617,#0f172a,#111827);
        color: white;
    }

    .main-title {
        text-align: center;
        font-size: 4rem;
        font-weight: 900;
        color: #22d3ee;
        text-shadow: 0px 0px 25px cyan;
        margin-bottom: 10px;
    }

    .subtitle {
        text-align: center;
        color: #cbd5e1;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }

    .feature-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0px 0px 15px rgba(34,211,238,0.15);
    }

    .info-box {
        background: rgba(34,211,238,0.08);
        border-left: 5px solid cyan;
        border-radius: 12px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------
# HEADER
# ------------------------------------------------------

st.markdown('<div class="main-title">🔐 Quantum Encryption Lab</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">Interactive BB84 Quantum Key Distribution Simulator with Real-Time Eavesdropping Detection</div>',
    unsafe_allow_html=True
)

# ------------------------------------------------------
# INTRODUCTION
# ------------------------------------------------------

with st.expander("📘 What does this simulator do?"):
    st.markdown(
        """
        This simulator demonstrates the **BB84 Quantum Key Distribution Protocol**, one of the first quantum encryption methods.

        ### How it works:
        1. Alice creates random quantum bits.
        2. These qubits travel through a quantum channel.
        3. Bob measures them using random bases.
        4. If Eve (an eavesdropper) intercepts the qubits, the quantum states change.
        5. The system detects the disturbance automatically.

        ### Why this matters:
        Quantum encryption enables communication systems where spying attempts become physically detectable.
        """
    )

# ------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------

st.sidebar.title("⚙ Simulation Settings")

num_bits = st.sidebar.slider(
    "Number of Qubits",
    min_value=8,
    max_value=128,
    value=32,
    help="Controls how many quantum bits are transmitted"
)

simulation_mode = st.sidebar.selectbox(
    "Simulation Mode",
    [
        "Secure Transmission",
        "Eavesdropping Attack"
    ]
)

simulate = st.sidebar.button("🚀 Launch Quantum Simulation", use_container_width=True)

# ------------------------------------------------------
# QUANTUM PROCESSOR STATUS
# ------------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.subheader("⚛ Quantum Processor")

cpu_load = random.randint(40, 97)
coherence = random.randint(70, 99)
noise = random.randint(1, 18)

st.sidebar.caption("Quantum Core Utilization")
st.sidebar.progress(cpu_load / 100)

st.sidebar.caption("Qubit Coherence Stability")
st.sidebar.progress(coherence / 100)

st.sidebar.caption("Noise Suppression")
st.sidebar.progress((100 - noise) / 100)

# ------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------


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
        temp_qc = qc.copy()

        if base == 'x':
            temp_qc.h(0)

        state = Statevector.from_instruction(temp_qc)
        probs = state.probabilities()

        measurement = np.random.choice([0, 1], p=probs)
        results.append(measurement)

    return np.array(results)

# ------------------------------------------------------
# MAIN SIMULATION
# ------------------------------------------------------

if simulate:

    eavesdrop = simulation_mode == "Eavesdropping Attack"

    # Alice
    alice_bits = generate_bits(num_bits)
    alice_bases = generate_bases(num_bits)

    qubits = encode_qubits(alice_bits, alice_bases)

    # Eve
    if eavesdrop:
        eve_bases = generate_bases(num_bits)
        eve_results = measure_qubits(qubits, eve_bases)
        qubits = encode_qubits(eve_results, eve_bases)

    # Bob
    bob_bases = generate_bases(num_bits)
    bob_results = measure_qubits(qubits, bob_bases)

    # Shared Key
    matching = alice_bases == bob_bases

    shared_key_alice = alice_bits[matching]
    shared_key_bob = bob_results[matching]

    errors = np.sum(shared_key_alice != shared_key_bob)

    error_rate = (
        (errors / len(shared_key_alice)) * 100
        if len(shared_key_alice) > 0 else 0
    )

    secure = error_rate < 15

    # ------------------------------------------------------
    # STATUS BANNER
    # ------------------------------------------------------

    if secure:
        st.success("✅ Secure quantum communication established successfully.")
    else:
        st.error("⚠ Quantum disturbance detected — possible eavesdropping attack.")

    # ------------------------------------------------------
    # METRICS
    # ------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Shared Key Length", len(shared_key_alice))
    c2.metric("Detected Errors", int(errors))
    c3.metric("Error Rate", f"{error_rate:.2f}%")
    c4.metric("Security", "SECURE" if secure else "COMPROMISED")

    # ------------------------------------------------------
    # PROBABILITY GRAPH
    # ------------------------------------------------------

    st.markdown("## 🌌 Quantum Probability States")

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
            textposition="outside"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        title="Probability of Measuring Quantum State |1⟩",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------
    # THREAT METER
    # ------------------------------------------------------

    st.markdown("## 🚨 Quantum Threat Analysis")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=error_rate,
        title={'text': "Threat Level"},
        gauge={
            'axis': {'range': [0, 30]},
            'bar': {'color': "cyan"},
            'steps': [
                {'range': [0, 10], 'color': '#00ff99'},
                {'range': [10, 20], 'color': '#ffaa00'},
                {'range': [20, 30], 'color': '#ff004c'}
            ]
        }
    ))

    gauge.update_layout()
     
