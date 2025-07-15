# Import required libraries
from dash import Dash
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
app = Dash()

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',  # <-- change here
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + [
                                        {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
                                    ],
                                    value='ALL',
                                    placeholder="place holder here",
                                    searchable=True
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
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,
                                    marks={
                                        int(min_payload): str(int(min_payload)),
                                        int(max_payload): str(int(max_payload)),
                                        2500: '2500',
                                        5000: '5000',
                                        7500: '7500'
                                    },
                                    value=[min_payload, max_payload]
                                ),


                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
from dash import Input, Output
import plotly.express as px


@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For ALL sites, show total success counts for each site
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',  # assuming 'class' is 1 for success and 0 for failure, might need aggregation
            title='Total Success Launches by Site'
        )
        return fig
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # Count success vs failure for this site
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']

        # Map class values to meaningful names
        success_counts['class'] = success_counts['class'].map({1: 'Success', 0: 'Failure'})

        # Pie chart for success vs failure for the selected site
        fig = px.pie(
            success_counts,
            names='class',
            values='count',
            title=f'Success vs Failure for site {entered_site}'
        )
        return fig

        # return the outcomes piechart for a selected site
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range  # unpack payload range from slider

    # Filter dataframe based on payload mass range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            symbol='class',  # <-- add this line to differentiate success/failure by symbol
            title='Payload vs Outcome for All Sites',
            labels={'class': 'Launch Outcome (0=Failure, 1=Success)'},
            hover_data=['Launch Site']
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            symbol='class',  # <-- differentiate success/failure by symbol here as well
            title=f'Payload vs Outcome for site {selected_site}',
            labels={'class': 'Launch Outcome (0=Failure, 1=Success)'},
            hover_data=['Launch Site']
        )

    # Optionally, you can update the symbol map for better clarity:
    fig.update_traces(marker=dict(size=10))  # you can adjust marker size

    # Update layout legend title for symbol
    fig.update_layout(
        legend_title_text='Booster Version & Outcome',
        legend=dict(
            itemsizing='constant',
        )
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
