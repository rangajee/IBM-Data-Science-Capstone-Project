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
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                id='site-dropdown',
                                options=([{'label': 'All Sites', 'value': 'ALL'}] +
                                        [{'label': s, 'value': s}
                                        for s in sorted(spacex_df['Launch Site'].unique())]),
                                value='ALL',                           # default to all sites
                                placeholder='Select a Launch Site here',
                                searchable=True,
                                clearable=False
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_success_pie(selected_site):
    # If ALL sites are selected, show total successful launches by site
    if selected_site == 'ALL':
        df_all = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            df_all,
            names='Launch Site',
            title='Total Success Launches By Site'
        )
        return fig
    else:
        # Filter data for the selected site
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = (
            df_site['class']
            .value_counts()
            .rename_axis('Outcome')
            .reset_index(name='Count')
            .replace({'Outcome': {1: 'Success', 0: 'Failure'}})
        )
        fig = px.pie(
            counts,
            names='Outcome',
            values='Count',
            title=f'Total Success vs Failure for site {selected_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    # Filter by payload range
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    # Filter by site (if not ALL)
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    title = (f'Payload vs. Outcome for {selected_site}'
             if selected_site != 'ALL' else
             'Payload vs. Outcome for All Sites')

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title,
        hover_data=['Launch Site']
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8060)
