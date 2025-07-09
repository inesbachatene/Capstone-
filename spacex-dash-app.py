# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # TÂCHE 1 : Dropdown pour sélectionner un site de lancement
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'Tous les sites', 'value': 'ALL'},
            *[
                {'label': site, 'value': site}
                for site in spacex_df['Launch Site'].unique()
            ]
        ],
        value='ALL',
        placeholder="Sélectionnez un site de lancement ici",
        searchable=True
    ),
    
    html.Br(),

    # TASK 2: Pie chart des succès des lancements selon le site choisi
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TÂCHE 3 : Slider de sélection de la charge utile
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2000)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # TASK 4: Scatter plot entre la charge utile et le succès
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TÂCHE 2 : Callback pour mettre à jour le graphique à secteurs en fonction du site sélectionné
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Pour tous les sites, afficher le total des lancements réussis par site
        df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df, values='class', names='Launch Site',
                     title='Nombre total de lancements réussis par site')
    else:
        # Filtrer pour le site sélectionné
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Compter le nombre de succès (class=1) et d’échecs (class=0)
        success_fail_counts = filtered_df['class'].value_counts().reset_index()
        success_fail_counts.columns = ['class', 'count']
        success_fail_counts['class'] = success_fail_counts['class'].map({1: 'Succès', 0: 'Échec'})
        fig = px.pie(success_fail_counts, values='count', names='class',
                     title=f'Taux de succès pour le site {entered_site}')
    return fig

# TÂCHE 4 : Callback pour mettre à jour le graphique de dispersion en fonction du site sélectionné et de la plage de charge utile
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_plot(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Corrélation entre charge utile et succès de lancement pour tous les sites',
            labels={'class': 'Succès (1) / Échec (0)'}
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Corrélation entre charge utile et succès pour le site {entered_site}',
            labels={'class': 'Succès (1) / Échec (0)'}
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)
