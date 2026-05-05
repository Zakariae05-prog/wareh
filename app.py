import streamlit as st
import pandas as pd
import math
import random

st.title("🏭 Smart Warehouse 4.0 - Adaptive AI System")

# =========================
# 🧠 SESSION STATE INIT
# =========================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Product": ["A", "B", "C", "D", "E"],
        "X": [3, 5, 2, 8, 6],
        "Y": [1, 2, 6, 3, 7],
        "Stock": [10, 8, 15, 5, 12],
        "Defect_rate": [0.1, 0.05, 0.2, 0.08, 0.12]
    })

if "history" not in st.session_state:
    st.session_state.history = []

if "order_path" not in st.session_state:
    st.session_state.order_path = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

data = st.session_state.data

# =========================
# 📊 DASHBOARD KPI
# =========================
st.subheader("📊 Dashboard KPI")

col1, col2, col3 = st.columns(3)

col1.metric("Stock Total", int(data["Stock"].sum()))
col2.metric("Produits", len(data))
col3.metric("Défaut moyen", round(data["Defect_rate"].mean(), 2))

st.dataframe(data)

# =========================
# 🛒 ORDER INPUT
# =========================
st.subheader("🛒 Nouvelle Commande")

order = st.multiselect(
    "Choisir produits",
    data["Product"].tolist()
)

# =========================
# 📏 DISTANCE
# =========================
def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# =========================
# 🚶 OPTIMISATION PICKING
# =========================
def optimize_path(order_list, df):
    path = []
    current = (0, 0)
    remaining = order_list.copy()

    while remaining:
        nearest = None
        min_d = float("inf")

        for p in remaining:
            row = df[df["Product"] == p].iloc[0]
            pos = (row["X"], row["Y"])
            d = distance(current, pos)

            if d < min_d:
                min_d = d
                nearest = p

        path.append(nearest)
        row = df[df["Product"] == nearest].iloc[0]
        current = (row["X"], row["Y"])
        remaining.remove(nearest)

    return path

# =========================
# 📈 DEMAND ANALYSIS
# =========================
def analyze_demand(history):
    demand = {}
    for p in history:
        demand[p] = demand.get(p, 0) + 1
    return demand

# =========================
# 📦 DYNAMIC LAYOUT OPTIMIZATION
# =========================
def optimize_layout(df, demand):
    if not demand:
        return df

    sorted_products = sorted(
        demand.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # zones proches entrée
    positions = [(0,0), (1,0), (0,1), (1,1), (2,0)]

    df = df.copy()

    for i, (product, _) in enumerate(sorted_products):
        if i < len(positions):
            df.loc[df["Product"] == product, "X"] = positions[i][0]
            df.loc[df["Product"] == product, "Y"] = positions[i][1]

    return df

# =========================
# 🚀 GENERATE ORDER
# =========================
if st.button("🚀 Générer Picking"):

    if not order:
        st.warning("Sélectionne au moins un produit")
    else:
        path = optimize_path(order, data)
        st.session_state.order_path = path

        st.success("✔ Picking optimisé")

        st.write("📍 Trajet opérateur :")
        st.write(" → ".join(path))

# =========================
# 📡 QR SCAN SIMULATION
# =========================
st.subheader("📡 Scan Produit")

scan_product = st.selectbox(
    "Scanner produit",
    data["Product"].tolist()
)

if st.button("📡 Scanner"):

    row = data[data["Product"] == scan_product].iloc[0]

    is_defect = random.random() < row["Defect_rate"]

    # enregistrer historique achat
    st.session_state.history.append(scan_product)

    if is_defect:
        alert = f"❌ {scan_product} DEFECTUEUX"
        st.session_state.alerts.append(alert)
        st.error(alert)
    else:
        st.success(f"✔ {scan_product} OK")

        # update stock
        st.session_state.data.loc[
            st.session_state.data["Product"] == scan_product,
            "Stock"
        ] -= 1

# =========================
# 🔄 AUTO LAYOUT OPTIMIZATION
# =========================
if st.button("🔄 Optimiser Layout (IA)"):
    demand = analyze_demand(st.session_state.history)
    st.session_state.data = optimize_layout(st.session_state.data, demand)
    st.success("📦 Layout réorganisé selon la demande")

# =========================
# 📊 DEMAND DASHBOARD
# =========================
st.subheader("📊 Analyse Historique")

if st.session_state.history:
    demand = analyze_demand(st.session_state.history)
    st.bar_chart(demand)
else:
    st.info("Aucun historique encore")

# =========================
# 🚨 ALERTS
# =========================
st.subheader("🚨 Alertes")

if st.session_state.alerts:
    for a in st.session_state.alerts:
        st.warning(a)
else:
    st.info("Aucune alerte")

# =========================
# 🚶 LAST PATH
# =========================
st.subheader("🚶 Dernier Trajet")

if st.session_state.order_path:
    st.write(" → ".join(st.session_state.order_path))
else:
    st.info("Aucun trajet")
