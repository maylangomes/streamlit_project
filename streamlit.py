import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
import plotly.figure_factory as ff

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Décès par département", page_icon=":chart_with_upwards_trend:", layout="wide")

st.title(":bar_chart: Total et pourcentage des décès par département en France (population légale déclarée par l'INSEE)")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

df = pd.read_csv("deces.csv", delimiter=';', encoding='utf-8')

df.columns = ["Zone", "Département", "Total_Deces2023", "Total_0_24ans_Deces2023", "Total_25_49ans_Deces2023",
       "Total_50_64ans_Deces2023", "Total_65_74ans_Deces2023", "Total_75_84ans_Deces2023", "Total_85ans_plus_Deces2023",
       "Total décès 2022", "0-24 ans", "25-49 ans", "50-64 ans",
       "65-74 ans", "75-84 ans", "85 ans et plus", "Total_Deces2019",
       "Total_0_24ans_Deces2019", "Total_25_49ans_Deces2019", "Total_50_64ans_Deces2019", "Total_65_74ans_Deces2019",
       "Total_75_84ans_Deces2019", "Total_85ans_plus_Deces2019", "Date_evenement", "Population"]

df = df[["Zone", "Département", "Total décès 2022", "0-24 ans", "25-49 ans",
         "50-64 ans", "65-74 ans", "75-84 ans",
         "85 ans et plus", "Population"]]

df.fillna('Unknown', inplace=True)

st.sidebar.header("Filtre :")
regions = st.sidebar.multiselect("Choisissez les départements", df["Département"].unique())

df["% de décès"] = (df["Total décès 2022"] / df["Population"]) * 100

if not regions:
    filtered_df = df.nlargest(10, "% de décès")
    title_suffix = " (Top 10 des % de décès les plus élevés)"
else:
    filtered_df = df[df["Département"].isin(regions)]
    selected_departments = ", ".join(regions)
    title_suffix = f" ({selected_departments})"

deces_par_zone = filtered_df.groupby(by=["Département"], as_index=False).agg(
    {"Total décès 2022": "sum", "Population": "first", "% de décès": "mean"})

col1, col2 = st.columns((2))
with col1:
    st.subheader(f"Pourcentage des décès par zone{title_suffix}")
    fig = px.bar(deces_par_zone, x="Département", y="% de décès", text="% de décès", template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=400)

with col2:
    st.subheader(f"Répartition des décès par zone{title_suffix}")
    fig = px.pie(filtered_df, values="Total décès 2022", names="Département", hole=0.5)
    fig.update_traces(text=filtered_df["Département"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander(f"Données par zone{title_suffix}"):
        st.write(deces_par_zone.style.background_gradient(cmap="Blues"))
        csv = deces_par_zone.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger les données", data=csv, file_name="Total_Deces_par_Zone.csv", mime="text/csv",
                          help="Cliquez ici pour télécharger les données au format CSV")

with cl2:
    with st.expander(f"Données détaillées{title_suffix}"):
        st.write(filtered_df.style.background_gradient(cmap="Oranges"))
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger les données", data=csv, file_name="Donnees_detaillees.csv", mime="text/csv",
                          help="Cliquez ici pour télécharger les données au format CSV")

st.subheader(f"Vue hiérarchique des décès par zone et tranche d'âge{title_suffix}")
# Préparer les données pour le treemap
df_melted = filtered_df.melt(id_vars=["Zone", "Département", "Population", "% de décès", "Total décès 2022"],
                             value_vars=["0-24 ans", "25-49 ans", "50-64 ans", "65-74 ans", "75-84 ans", "85 ans et plus"],
                             var_name="Tranche d'âge", value_name="Décès par tranche d'âge")

fig3 = px.treemap(df_melted, path=["Département", "Tranche d'âge"], values="Décès par tranche d'âge",
                  hover_data=["Total décès 2022", "% de décès"], color="Décès par tranche d'âge")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader(f"Total des décès par groupe d'âge{title_suffix}")
    fig = px.bar(filtered_df, x="Département", y=["0-24 ans", "25-49 ans", "50-64 ans",
                                                 "65-74 ans", "75-84 ans", "85 ans et plus"],
                 barmode="stack", template="gridon")
    st.plotly_chart(fig, use_container_width=True)

st.subheader(f":point_right: Tableau récapitulatif des décès{title_suffix}")
with st.expander(f"Récapitulatif avec pourcentage et total par âge et par département{title_suffix}"):
    st.markdown("Détails des décès par zone")
    details_deces_zone = pd.pivot_table(data=filtered_df, values=["Total décès 2022", "0-24 ans", "25-49 ans",
                                                                  "50-64 ans", "65-74 ans", "75-84 ans", "85 ans et plus", "Population", "% de décès"],
                                        index=["Département"], aggfunc="sum")
    st.write(details_deces_zone.style.background_gradient(cmap="Blues"))
