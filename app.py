import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime

st.set_page_config(
    page_title="HDEP PFMEA Control Center",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# HDEP PFMEA CONTROL CENTER
# TE Connectivity - HDEP 12.8L / 14.2L
# Streamlit application
# ============================================================

# ------------------------- STYLE -----------------------------
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
    }
    .subtitle {
        color: #666;
        margin-bottom: 1.2rem;
    }
    .kpi {
        padding: 18px;
        border-radius: 12px;
        background: #f7f7f7;
        border: 1px solid #e4e4e4;
        text-align: center;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
    }
    .kpi-label {
        color: #666;
        font-size: 0.9rem;
    }
    .risk-high { color: #b00020; font-weight: 800; }
    .risk-medium { color: #c77700; font-weight: 800; }
    .risk-low { color: #287a32; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ------------------------- PROCESS ---------------------------
PROCESS_STEPS = [
    "Réception / Stockage",
    "Coupe",
    "Préparation / Splicing",
    "Emmanchement / Sertissage",
    "Torsadage",
    "Assemblage",
    "Insertion & Push-back",
    "EOL Test",
    "Contrôle",
    "Packaging"
]

MACHINES = {
    "Réception / Stockage": "Magasin / zone logistique",
    "Coupe": "Komax Alpha 550T",
    "Préparation / Splicing": "SS-2FP",
    "Emmanchement / Sertissage": "Poste de préparation / sertissage",
    "Torsadage": "BT 188T",
    "Assemblage": "Postes d'assemblage",
    "Insertion & Push-back": "Poste insertion / fixation",
    "EOL Test": "Banc EOL",
    "Contrôle": "Poste contrôle",
    "Packaging": "Poste emballage"
}

# ------------------------- DEFAULT PFMEA ---------------------
# Exemple de structure. Les valeurs doivent être validées avec
# la PFMEA officielle de l'entreprise avant utilisation industrielle.
DEFAULT_ROWS = [
    {
        "Processus": "Coupe",
        "Fonction": "Couper le fil à la longueur spécifiée",
        "Mode de défaillance": "Longueur de fil incorrecte",
        "Effet": "Non-conformité du faisceau / problème d'assemblage",
        "Cause": "Mauvais réglage / mauvais paramètre machine",
        "Prévention": "Standard de réglage + paramètres validés",
        "Détection": "Contrôle longueur / contrôle première pièce",
        "S": 7, "O": 4, "D": 3,
        "Action": "Vérifier le réglage et standardiser le contrôle première pièce",
        "Responsable": "Process",
        "Échéance": str(date.today()),
        "Statut": "En cours"
    },
    {
        "Processus": "Emmanchement / Sertissage",
        "Fonction": "Assurer la connexion correcte du contact",
        "Mode de défaillance": "Sertissage insuffisant",
        "Effet": "Mauvaise connexion électrique / risque client",
        "Cause": "Paramètre de sertissage incorrect / outil usé",
        "Prévention": "Paramètres standardisés + maintenance outil",
        "Détection": "Contrôle sertissage / pull test",
        "S": 9, "O": 3, "D": 4,
        "Action": "Renforcer le contrôle des paramètres et du moyen de sertissage",
        "Responsable": "Process / Qualité",
        "Échéance": str(date.today()),
        "Statut": "En cours"
    },
    {
        "Processus": "Torsadage",
        "Fonction": "Réaliser la torsade selon la spécification",
        "Mode de défaillance": "Torsade non conforme",
        "Effet": "Non-conformité fonctionnelle / assemblage difficile",
        "Cause": "Réglage machine / mauvais positionnement du câble",
        "Prévention": "Standard de réglage",
        "Détection": "Contrôle visuel + mesure",
        "S": 7, "O": 3, "D": 4,
        "Action": "Standardiser les paramètres et le contrôle",
        "Responsable": "Process",
        "Échéance": str(date.today()),
        "Statut": "Non commencé"
    },
    {
        "Processus": "Assemblage",
        "Fonction": "Assembler correctement la pièce complète",
        "Mode de défaillance": "Mauvais assemblage",
        "Effet": "Produit non conforme / rework / scrap",
        "Cause": "Méthode opératoire / positionnement / variation opérateur",
        "Prévention": "Instruction de travail + formation",
        "Détection": "Contrôle visuel / contrôle poste",
        "S": 8, "O": 5, "D": 4,
        "Action": "Standardiser le travail et équilibrer les tâches",
        "Responsable": "Process",
        "Échéance": str(date.today()),
        "Statut": "En cours"
    },
    {
        "Processus": "Insertion & Push-back",
        "Fonction": "Insérer et fixer correctement les fils dans le connecteur",
        "Mode de défaillance": "Fil mal positionné / endommagé",
        "Effet": "Défaut électrique / non-conformité / risque client",
        "Cause": "Fixation manuelle difficile / outil inadapté",
        "Prévention": "Moyen de fixation adapté + standard opératoire",
        "Détection": "Contrôle visuel + contrôle push-back",
        "S": 9, "O": 5, "D": 5,
        "Action": "Étudier et valider un outil de fixation des fils",
        "Responsable": "Process",
        "Échéance": str(date.today()),
        "Statut": "En cours"
    },
    {
        "Processus": "EOL Test",
        "Fonction": "Tester la conformité électrique",
        "Mode de défaillance": "Défaut non détecté",
        "Effet": "Produit non conforme livré au client",
        "Cause": "Paramètre de test / défaut moyen de contrôle",
        "Prévention": "Validation du programme de test",
        "Détection": "Test EOL",
        "Action": "Vérifier périodiquement le moyen de test",
        "Responsable": "Qualité / Process",
        "Échéance": str(date.today()),
        "Statut": "Non commencé"
    },
    {
        "Processus": "Packaging",
        "Fonction": "Conditionner le produit conformément aux exigences",
        "Mode de défaillance": "Mauvais conditionnement",
        "Effet": "Endommagement / problème logistique",
        "Cause": "Mauvaise méthode / emballage incorrect",
        "Prévention": "Standard packaging",
        "Détection": "Contrôle final",
        "S": 6, "O": 2, "D": 3,
        "Action": "Standardiser le conditionnement",
        "Responsable": "Production / Qualité",
        "Échéance": str(date.today()),
        "Statut": "Terminé"
    }
]

# ------------------------- SESSION ----------------------------
if "pfmea" not in st.session_state:
    st.session_state.pfmea = pd.DataFrame(DEFAULT_ROWS)

if "history" not in st.session_state:
    st.session_state.history = []

if "actions" not in st.session_state:
    st.session_state.actions = []

# ------------------------- FUNCTIONS -------------------------
def normalize_pfmea(df):
    required = [
        "Processus", "Fonction", "Mode de défaillance", "Effet", "Cause",
        "Prévention", "Détection", "S", "O", "D", "Action",
        "Responsable", "Échéance", "Statut"
    ]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    for col in ["S", "O", "D"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(1).clip(1, 10).astype(int)
    df["IPR"] = df["S"] * df["O"] * df["D"]
    return df[required + ["IPR"]]

def risk_level(ipr):
    if ipr >= 150:
        return "Élevé"
    if ipr >= 80:
        return "Moyen"
    return "Faible"

def risk_symbol(ipr):
    level = risk_level(ipr)
    return {"Élevé": "🔴", "Moyen": "🟠", "Faible": "🟢"}[level]

def add_history():
    df = normalize_pfmea(st.session_state.pfmea.copy())
    st.session_state.history.append({
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "IPR moyen": round(df["IPR"].mean(), 1) if len(df) else 0,
        "IPR max": int(df["IPR"].max()) if len(df) else 0,
        "Risques élevés": int((df["IPR"] >= 150).sum()),
        "Actions ouvertes": int((df["Statut"] != "Terminé").sum())
    })

# ------------------------- SIDEBAR ---------------------------
st.sidebar.title("🔴 HDEP PFMEA")
st.sidebar.caption("TE Connectivity — outil de démonstration")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "🔄 Process Flow",
        "🔴 PFMEA",
        "🔧 Action Plan",
        "📈 Risk Evolution",
        "📥 Import / Export"
    ]
)

st.sidebar.divider()
st.sidebar.info(
    "Application dédiée à l'analyse des risques process de la ligne HDEP. "
    "Les données d'exemple doivent être remplacées/validées par les données officielles."
)

# ============================================================
# DASHBOARD
# ============================================================
if page == "📊 Dashboard":
    st.markdown('<div class="main-title">HDEP PFMEA Control Center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Pilotage dynamique des risques process de la ligne HDEP</div>',
        unsafe_allow_html=True
    )

    df = normalize_pfmea(st.session_state.pfmea.copy())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Modes de défaillance", len(df))
    c2.metric("Risques élevés", int((df["IPR"] >= 150).sum()))
    c3.metric("IPR moyen", round(df["IPR"].mean(), 1) if len(df) else 0)
    c4.metric(
        "Actions terminées",
        f"{(df['Statut'].eq('Terminé').mean()*100):.0f}%" if len(df) else "0%"
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pareto des risques par poste")
        if len(df):
            g = df.groupby("Processus", as_index=False)["IPR"].sum().sort_values("IPR", ascending=False)
            fig = px.bar(g, x="IPR", y="Processus", orientation="h", text="IPR")
            fig.update_layout(height=430, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Répartition des niveaux de risque")
        if len(df):
            levels = df["IPR"].apply(risk_level).value_counts().reindex(
                ["Élevé", "Moyen", "Faible"], fill_value=0
            ).reset_index()
            levels.columns = ["Niveau", "Nombre"]
            fig = px.pie(levels, names="Niveau", values="Nombre", hole=0.45)
            fig.update_layout(height=430)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚨 Top 10 des risques")
    top = df.sort_values("IPR", ascending=False).head(10).copy()
    top["Niveau"] = top["IPR"].apply(risk_level)
    top["Criticité"] = top["IPR"].apply(risk_symbol)
    st.dataframe(
        top[
            ["Criticité", "Processus", "Mode de défaillance",
             "Effet", "S", "O", "D", "IPR", "Niveau", "Statut"]
        ],
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# PROCESS FLOW
# ============================================================
elif page == "🔄 Process Flow":
    st.title("🔄 Process Flow — Ligne HDEP")

    st.write(
        "Sélectionnez un poste pour visualiser ses informations et les risques PFMEA associés."
    )

    selected = st.selectbox("Poste", PROCESS_STEPS)
    df = normalize_pfmea(st.session_state.pfmea.copy())
    sub = df[df["Processus"] == selected]

    st.subheader(selected)
    a, b, c = st.columns(3)
    a.metric("Machine / moyen", MACHINES.get(selected, "À renseigner"))
    b.metric("Modes de défaillance", len(sub))
    c.metric("IPR maximum", int(sub["IPR"].max()) if len(sub) else 0)

    st.divider()

    st.subheader("Informations process")
    st.info(
        f"**Poste :** {selected}\n\n"
        f"**Moyen :** {MACHINES.get(selected, 'À renseigner')}\n\n"
        "**Produit :** HDEP 12.8L / 14.2L — PN produit à confirmer selon la version étudiée."
    )

    st.subheader("Risques associés")
    if len(sub):
        view = sub.copy()
        view["Niveau"] = view["IPR"].apply(risk_level)
        view["Criticité"] = view["IPR"].apply(risk_symbol)
        st.dataframe(
            view[
                ["Criticité", "Mode de défaillance", "Effet", "Cause",
                 "S", "O", "D", "IPR", "Niveau"]
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Aucune analyse PFMEA n'est encore enregistrée pour ce poste.")

# ============================================================
# PFMEA
# ============================================================
elif page == "🔴 PFMEA":
    st.title("🔴 PFMEA — Analyse des risques process")

    st.caption(
        "S = Sévérité | O = Occurrence | D = Détection. "
        "L'IPR est calculé automatiquement."
    )

    df = normalize_pfmea(st.session_state.pfmea.copy())

    with st.expander("➕ Ajouter un nouveau mode de défaillance", expanded=False):
        with st.form("add_failure", clear_on_submit=True):
            c1, c2 = st.columns(2)
            processus = c1.selectbox("Processus", PROCESS_STEPS)
            fonction = c2.text_input("Fonction")

            c1, c2 = st.columns(2)
            mode = c1.text_input("Mode de défaillance")
            effet = c2.text_input("Effet")

            c1, c2 = st.columns(2)
            cause = c1.text_input("Cause")
            prevention = c2.text_input("Action de prévention")

            c1, c2 = st.columns(2)
            detection = c1.text_input("Moyen de détection")
            action = c2.text_input("Action recommandée")

            c1, c2, c3 = st.columns(3)
            s = c1.number_input("Sévérité (S)", 1, 10, 5)
            o = c2.number_input("Occurrence (O)", 1, 10, 3)
            d = c3.number_input("Détection (D)", 1, 10, 3)

            c1, c2 = st.columns(2)
            responsable = c1.text_input("Responsable", "Process")
            echeance = c2.date_input("Échéance", date.today())

            statut = st.selectbox(
                "Statut",
                ["Non commencé", "En cours", "Terminé"]
            )

            submitted = st.form_submit_button("Ajouter à la PFMEA")

            if submitted:
                if not mode.strip():
                    st.error("Le mode de défaillance est obligatoire.")
                else:
                    new_row = {
                        "Processus": processus,
                        "Fonction": fonction,
                        "Mode de défaillance": mode,
                        "Effet": effet,
                        "Cause": cause,
                        "Prévention": prevention,
                        "Détection": detection,
                        "S": int(s),
                        "O": int(o),
                        "D": int(d),
                        "Action": action,
                        "Responsable": responsable,
                        "Échéance": str(echeance),
                        "Statut": statut
                    }
                    st.session_state.pfmea = pd.concat(
                        [st.session_state.pfmea, pd.DataFrame([new_row])],
                        ignore_index=True
                    )
                    add_history()
                    st.success("Mode de défaillance ajouté.")

    st.subheader("Tableau PFMEA")

    # Filters
    f1, f2, f3 = st.columns(3)
    filter_process = f1.multiselect(
        "Filtrer par poste",
        PROCESS_STEPS,
        default=[]
    )
    filter_risk = f2.multiselect(
        "Niveau de risque",
        ["Élevé", "Moyen", "Faible"],
        default=[]
    )
    filter_status = f3.multiselect(
        "Statut",
        ["Non commencé", "En cours", "Terminé"],
        default=[]
    )

    view = df.copy()
    if filter_process:
        view = view[view["Processus"].isin(filter_process)]
    if filter_risk:
        view = view[view["IPR"].apply(risk_level).isin(filter_risk)]
    if filter_status:
        view = view[view["Statut"].isin(filter_status)]

    view["Niveau"] = view["IPR"].apply(risk_level)
    view["Criticité"] = view["IPR"].apply(risk_symbol)

    st.dataframe(
        view[
            ["Criticité", "Processus", "Fonction", "Mode de défaillance",
             "Effet", "Cause", "S", "O", "D", "IPR", "Niveau",
             "Action", "Responsable", "Échéance", "Statut"]
        ],
        use_container_width=True,
        hide_index=True,
        height=560
    )

    st.subheader("Modifier une analyse")
    if len(st.session_state.pfmea):
        row_id = st.number_input(
            "Index de la ligne à modifier",
            min_value=0,
            max_value=len(st.session_state.pfmea)-1,
            value=0,
            step=1
        )

        current = st.session_state.pfmea.iloc[int(row_id)]

        with st.form("edit_pfmea"):
            c1, c2 = st.columns(2)
            edit_s = c1.number_input("S", 1, 10, int(current["S"]))
            edit_o = c2.number_input("O", 1, 10, int(current["O"]))

            c1, c2 = st.columns(2)
            edit_d = c1.number_input("D", 1, 10, int(current["D"]))
            edit_status = c2.selectbox(
                "Statut",
                ["Non commencé", "En cours", "Terminé"],
                index=["Non commencé", "En cours", "Terminé"].index(
                    current["Statut"] if current["Statut"] in ["Non commencé", "En cours", "Terminé"] else "En cours"
                )
            )

            edit_action = st.text_area(
                "Action",
                str(current["Action"])
            )
            edit_responsable = st.text_input(
                "Responsable",
                str(current["Responsable"])
            )

            if st.form_submit_button("Enregistrer la modification"):
                st.session_state.pfmea.at[int(row_id), "S"] = int(edit_s)
                st.session_state.pfmea.at[int(row_id), "O"] = int(edit_o)
                st.session_state.pfmea.at[int(row_id), "D"] = int(edit_d)
                st.session_state.pfmea.at[int(row_id), "Action"] = edit_action
                st.session_state.pfmea.at[int(row_id), "Responsable"] = edit_responsable
                st.session_state.pfmea.at[int(row_id), "Statut"] = edit_status
                add_history()
                st.success("PFMEA mise à jour.")

# ============================================================
# ACTION PLAN
# ============================================================
elif page == "🔧 Action Plan":
    st.title("🔧 Plan d'actions")

    df = normalize_pfmea(st.session_state.pfmea.copy())
    df["Niveau"] = df["IPR"].apply(risk_level)

    open_df = df[df["Statut"] != "Terminé"].copy()

    c1, c2, c3 = st.columns(3)
    c1.metric("Actions ouvertes", len(open_df))
    c2.metric("Actions en retard", 0)
    c3.metric("Actions terminées", int((df["Statut"] == "Terminé").sum()))

    st.divider()

    st.subheader("Priorités")
    if len(open_df):
        priority = open_df.sort_values("IPR", ascending=False).copy()
        priority["Criticité"] = priority["IPR"].apply(risk_symbol)

        st.dataframe(
            priority[
                ["Criticité", "Processus", "Mode de défaillance",
                 "IPR", "Niveau", "Action", "Responsable",
                 "Échéance", "Statut"]
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("Toutes les actions sont terminées.")

    st.subheader("Suivi du taux de clôture")
    if len(df):
        completed = int((df["Statut"] == "Terminé").sum())
        total = len(df)
        progress = completed / total
        st.progress(progress)
        st.write(f"**{completed}/{total} actions terminées — {progress*100:.1f}%**")

# ============================================================
# RISK EVOLUTION
# ============================================================
elif page == "📈 Risk Evolution":
    st.title("📈 Évolution du risque")

    df = normalize_pfmea(st.session_state.pfmea.copy())

    if len(st.session_state.history) == 0:
        add_history()

    hist = pd.DataFrame(st.session_state.history)

    if len(hist):
        st.subheader("Évolution de l'IPR")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist["Date"],
            y=hist["IPR moyen"],
            mode="lines+markers",
            name="IPR moyen"
        ))
        fig.add_trace(go.Scatter(
            x=hist["Date"],
            y=hist["IPR max"],
            mode="lines+markers",
            name="IPR maximum"
        ))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="IPR",
            height=430
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Historique")
        st.dataframe(hist, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📌 Avant / Après — risque par poste")

    if len(df):
        grouped = df.groupby("Processus", as_index=False).agg(
            IPR=("IPR", "sum"),
            IPR_moyen=("IPR", "mean")
        ).sort_values("IPR", ascending=False)

        st.dataframe(grouped, use_container_width=True, hide_index=True)

# ============================================================
# IMPORT / EXPORT
# ============================================================
elif page == "📥 Import / Export":
    st.title("📥 Import / Export")

    st.subheader("Importer une PFMEA Excel")
    st.write(
        "Le fichier doit contenir au minimum les colonnes : "
        "Processus, Fonction, Mode de défaillance, Effet, Cause, "
        "Prévention, Détection, S, O, D, Action, Responsable, Échéance, Statut."
    )

    uploaded = st.file_uploader(
        "Choisir un fichier Excel",
        type=["xlsx", "xls"]
    )

    if uploaded is not None:
        try:
            imported = pd.read_excel(uploaded)
            imported = normalize_pfmea(imported)

            st.write("Aperçu du fichier importé")
            st.dataframe(imported, use_container_width=True, hide_index=True)

            if st.button("Remplacer la PFMEA actuelle par le fichier importé"):
                st.session_state.pfmea = imported.drop(columns=["IPR"])
                add_history()
                st.success("PFMEA importée avec succès.")
        except Exception as e:
            st.error(f"Erreur d'import : {e}")

    st.divider()

    st.subheader("Exporter la PFMEA")

    export_df = normalize_pfmea(st.session_state.pfmea.copy())
    export_df["Niveau"] = export_df["IPR"].apply(risk_level)

    excel_buffer = None
    try:
        import io
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="PFMEA")
            export_df[export_df["IPR"] >= 150].to_excel(
                writer, index=False, sheet_name="Risques_Eleves"
            )
            export_df[export_df["Statut"] != "Terminé"].to_excel(
                writer, index=False, sheet_name="Actions_Ouvertes"
            )
        excel_buffer.seek(0)

        st.download_button(
            "⬇️ Télécharger la PFMEA Excel",
            data=excel_buffer,
            file_name="HDEP_PFMEA.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Erreur de génération Excel : {e}")

    st.subheader("Exporter en CSV")
    csv = export_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Télécharger CSV",
        data=csv,
        file_name="HDEP_PFMEA.csv",
        mime="text/csv"
    )

    st.divider()

    if st.button("⚠️ Réinitialiser avec les données d'exemple"):
        st.session_state.pfmea = pd.DataFrame(DEFAULT_ROWS)
        st.session_state.history = []
        st.success("PFMEA réinitialisée.")

# ------------------------- FOOTER ---------------------------
st.sidebar.divider()
st.sidebar.caption("HDEP PFMEA Control Center • Streamlit")
