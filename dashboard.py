from dash import Dash, html, Output, Input, dcc
import dash_bootstrap_components as dbc
import plotly.express as px

import pandas as pd
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv('games.csv')
# Choose projects since 2000 to 2022
df = df[(df['Year_of_Release'] >= 2000) & (df['Year_of_Release'] <= 2022)]
# Delete rows which have missing values
df.dropna(inplace=True)
# Convert to float type
df['User_Score'] = pd.to_numeric(df['User_Score'], errors='coerce')
# Convert rating to numbers, where E - everyone may play,
# M - allowed to play from 17 years old, etc
df.Rating = df.Rating.replace(['E', 'M', 'T', 'E10+', 'AO', 'RP'],
                              [0, 17, 13, 10, 18, 0])
# Sorting
df = df.sort_values('Year_of_Release')
# Filter
platforms = df["Platform"].unique()
genres = df["Genre"].unique()
years = sorted(df["Year_of_Release"].unique())
start_year = 2000
end_year = 2022

app = Dash(__name__)

app.layout = html.Div([
        # Head
        html.Div([
            html.H1(children='Gaming industry analytics', style={'text-align': 'left'}),
            html.P(['The dashboard allows you to look at indicators such as the number of games, average ratings of players and critics, '
                   'and average rating'
                   ' by platform and genre for the selected time interval.',
                    html.Br()]),

                         ], style={'border': f'1px solid green', 'padding': '10px'}
                 ),
            # Average rating
            dbc.Card(dbc.Row([
                             dbc.Col(
                                 dcc.Graph(id='fig6', style={'float':'right', "height": "80%",
                                                             'boxShadow': '#e3e3e3 4px 4px 4px 4px'}))
                                 ])),
            # Filters
            html.Div([
            html.H4("Платформа"),
            dcc.Dropdown(
                id="platform_filter",
                options=[{'label': platform, 'value': platform} for platform in platforms],
                value=[platforms[0], platforms[1], platforms[2]],
                multi=True,
                placeholder='Choose platform', style={'width': '50%','fontWeight': 'bold'}),
                      ]),

            html.Div([
                html.H4("Game genre"),
                dcc.Dropdown(
                    id="genre_filter",
                    options=[{'label': genre, 'value': genre} for genre in genres],
                    value=[genres[0], genres[1], genres[2]],
                    multi=True,
                    placeholder='Choose genre'
                ), ], style={'width': '25%','fontWeight': 'bold'}),
            html.Div([
                html.H4("Year interval"),
                dcc.RangeSlider(
                            id='year_filter',
                            min=years[0],
                            max=years[-1],
                            step=1,
                            marks={int(year): str(year) for year in range(start_year, end_year + 1, 3)},
                            value=[years[0], years[-1]]
                    )], style={'width': '30%', 'fontWeight': 'bold', 'height':'100px',}),
            # Calculation of numerical values
            html.Div([
                html.Div([
                    html.P('Total number of games:'),
                    html.Div(id='games_number')
                ], style={'padding': '1px', 'margin': '1px','text-align': 'center',
                          'fontWeight': 'bold', 'boxShadow': '#e3e3e3 4px 4px 2px'}),
                html.Div([
                            html.P('Average player rating:'),
                            html.Div(id='avg_players_score')
                    ], style={'padding': '1px', 'margin': '1px', 'text-align': 'center',
                              'fontWeight': 'bold', 'boxShadow': '#e3e3e3 4px 4px 2px'}),

                    html.Div([
                        html.P('Average critic rating:'),
                        html.Div(id='avg_critic_score')
                    ], style={ 'padding': '1px', 'margin': '1px', 'text-align': 'center',
                              'fontWeight': 'bold', 'boxShadow': '#e3e3e3 4px 4px 2px'}),
                                ], style={'display': 'grid', 'grid-template-columns': '30vh 30vh 30vh',
                                          'border-radius': '5px 5px 5px', 'marginTop': '2rem', 'height':'6'}),
            # Game releases by year and platform
            # and Player and critic ratings by genre
            dbc.Container([dbc.Row([
                             dbc.Col(
                                    dbc.Card(dcc.Graph(id='fig4',
                                    style={'float':'left', "height": "auto", 'width':'6',
                                           'boxShadow': '#e3e3e3 4px 4px 4px 4px',
                                           'margin-bottom':'20px', 'margin-top':'90px'})))
                                        ]),
                        dbc.Row([
                            dbc.Col(
                                dcc.Graph(id='fig5', style={'float':'right', "height": "auto", 'width':'6',
                                                            'boxShadow': '#e3e3e3 4px 4px 4px 4px',
                                                            'margin-bottom':'20px', 'margin-top':'60px'}))

                           ])
            ])
        ])

@app.callback(
    [
        Output('games_number', 'children'),
        Output('avg_players_score', 'children'),
        Output('avg_critic_score', 'children'),
        Output('fig4', 'figure'),
        Output('fig5', 'figure'),
        Output('fig6', 'figure')
    ],
    [
        Input('platform_filter', 'value'),
        Input('genre_filter', 'value'),
        Input('year_filter', 'value')
    ]
)

def dashboard(platform, genre, interval):
    filtered_df = df.copy()
    if platform:
        filtered_df = filtered_df[filtered_df['Platform'].isin(platform)]

    if genre:
        filtered_df = filtered_df[filtered_df['Genre'].isin(genre)]

    if interval:
        filtered_df = filtered_df[(filtered_df['Year_of_Release'] >= interval[0])
                                  & (filtered_df['Year_of_Release'] <= interval[1])]

    # Total number of games
    games_number = filtered_df['Name'].count()
    # Overall Average Player Score
    avg_user_score = round(filtered_df['User_Score'].mean(), 2)
    # Overall average critic rating
    avg_critic_score = round(filtered_df['Critic_Score'].mean(), 2)
    # Stacked area plot showing game releases by year and platform.
    fig4 = px.area(filtered_df, x='Year_of_Release', y='Name',
                   color_discrete_sequence=px.colors.diverging.Temps,
                   color='Platform', title='Game releases by year and platform',
                   labels={'Name': 'Game name', 'Year_of_Release':'Year of release'})
    # Scatter plot broken down by genre.
    # On the X-axis - player ratings, on the Y-axis - critics' ratings.
    fig5 = px.scatter(filtered_df, x='User_Score', y='Critic_Score',
                      color='Genre', color_discrete_sequence=px.colors.diverging.Temps,
                      title='Player and critic ratings by genre',
                      labels={'Critic_Score': 'Critics score', 'User_Score':'User score'})
    # Bar/Line chart, average age rating by genre
    avg_rating = filtered_df.groupby('Genre', as_index=False)['Rating'].mean()
    fig6 = px.bar(avg_rating, x='Genre', y='Rating', color_discrete_sequence=px.colors.diverging.Temps,
                  title='Average age rating by genre')

    return games_number, avg_user_score, avg_critic_score, fig4, fig5, fig6


if __name__ == "__main__":
    app.run_server(debug=True)

