# dashboard.py
import pandas as pd
import plotly.express as px

# Charger le catalogue
df = pd.read_csv('data/rag_seed/rag_seed_catalog.csv')

# Graphiques
fig1 = px.pie(df, names='matiere', title='Distribution par Matière')
fig2 = px.bar(df.groupby('langue').size().reset_index(), x='langue', y=0, title='Documents par Langue')
fig3 = px.sunburst(df, path=['grade_level', 'matiere'], title='Hiérarchie des Documents')

# Afficher
fig1.show()
fig2.show()
fig3.show()