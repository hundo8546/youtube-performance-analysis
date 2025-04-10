import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import wordninja

df = pd.read_csv('shap_values.csv')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Impact on YouTube Engagement", style={'textAlign': 'center'}),

    html.Button("View Box Plot for Feature Importance for YouTube Engagement", id="toggle-boxplot-button", n_clicks=0, style={'margin': '20px'}),
    dbc.Collapse(
        id='boxplot-collapse',
        is_open=False,
        children=[
            html.Div([
                html.Label("Select Year:"),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': str(year), 'value': year} for year in sorted(df['year'].unique())],
                    value=sorted(df['year'].unique())[0],
                    style={'width': '200px'}
                )
            ], style={'margin': '20px'}),
            dcc.Graph(id='shap-boxplot', style={'height': '800px'})
        ]
    ),

    html.Button("View Line Graph for Mean Feature Importance Over Time", id="toggle-linegraph-button", n_clicks=0, style={'margin': '20px'}),
    dbc.Collapse(
        id='linegraph-collapse',
        is_open=False,
        children=[
            html.Div([
                html.Label("Select Category:"),
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[
                        {'label': " ".join([word.title() for word in wordninja.split(var)]), 'value': var}
                        for var in df['variable'].unique()
                    ],
                    value=df['variable'].unique()[0],
                    style={'width': '200px'}
                )
            ], style={'margin': '20px'}),
            dcc.Graph(id='line-graph', style={'height': '600px'})
        ]
    )
])

@app.callback(
    Output('boxplot-collapse', 'is_open'),
    Input('toggle-boxplot-button', 'n_clicks'),
    State('boxplot-collapse', 'is_open')
)
def toggle_boxplot_collapse(n_clicks, is_open):
    if n_clicks and n_clicks > 0:
        return not is_open
    return is_open

@app.callback(
    Output('linegraph-collapse', 'is_open'),
    Input('toggle-linegraph-button', 'n_clicks'),
    State('linegraph-collapse', 'is_open')
)
def toggle_linegraph_collapse(n_clicks, is_open):
    if n_clicks and n_clicks > 0:
        return not is_open
    return is_open

@app.callback(
    Output('shap-boxplot', 'figure'),
    Input('year-dropdown', 'value')
)
def update_boxplot(selected_year):
    filtered_df = df[df['year'] == selected_year]
    filtered_df = filtered_df[~filtered_df['variable'].str.startswith('posted_day_')]
    filtered_df['variable'] = filtered_df['variable'].apply(
        lambda x: " ".join([word.title() for word in wordninja.split(x)])
    )
    variables = filtered_df.groupby('variable')['value'].mean().sort_values(ascending=False).index.tolist()
    fig = go.Figure()

    for variable in variables:
        var_data = filtered_df[filtered_df['variable'] == variable]['value']
        if len(var_data) > 0:
            min_val = var_data.min()
            max_val = var_data.max()
            mean_val = var_data.mean()
            median_val = var_data.median()
            q1_val = var_data.quantile(0.25)
            q3_val = var_data.quantile(0.75)
            iqr = q3_val - q1_val
            lower_whisker = max(min_val, q1_val - 1.5 * iqr)
            upper_whisker = min(max_val, q3_val + 1.5 * iqr)
            color = 'blue' if mean_val > 0 else 'orange' if mean_val < 0 else 'grey'
            fig.add_trace(go.Box(
                y=[variable] * len(var_data),
                x=var_data,
                name=variable,
                orientation='h',
                fillcolor=color,
                opacity=0.6,
                line=dict(color='black'),
                boxmean=True,
                whiskerwidth=0.7,
                hoverinfo='skip'
            ))
            fig.add_trace(go.Scatter(
                x=[mean_val],
                y=[variable],
                mode='markers',
                marker=dict(size=0.1, opacity=0),
                showlegend=False,
                hovertemplate=(
                        f"<b>{variable}</b><br>" +
                        f"Min: {min_val:.4f}<br>" +
                        f"Lower Whisker: {lower_whisker:.4f}<br>" +
                        f"Q1: {q1_val:.4f}<br>" +
                        f"Median: {median_val:.4f}<br>" +
                        f"Mean: {mean_val:.4f}<br>" +
                        f"Q3: {q3_val:.4f}<br>" +
                        f"Upper Whisker: {upper_whisker:.4f}<br>" +
                        f"Max: {max_val:.4f}<br>" +
                        f"IQR: {iqr:.4f}" +
                        "<extra></extra>"
                )
            ))


    fig.update_layout(
        title=f"Feature Importance for YouTube Engagement ({selected_year})",
        xaxis_title="SHAP Values (Feature Importance)",
        yaxis_title="Features",
        showlegend=False,
        height=600,
        margin=dict(l=150, r=50, t=100, b=100)
    )

    return fig

@app.callback(
    Output('line-graph', 'figure'),
    Input('category-dropdown', 'value')
)
def update_line_graph(selected_category):
    filtered_df = df[df['variable'] == selected_category]
    mean_shap = filtered_df.groupby('year')['value'].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mean_shap['year'],
        y=mean_shap['value'],
        mode='lines+markers',
        name=selected_category
    ))

    fig.update_layout(
        title=f"Mean Feature Importance Over Time for {selected_category}",
        xaxis_title="Year",
        yaxis_title="Mean SHAP Value",
        showlegend=False,
        height=600,
        margin=dict(l=50, r=50, t=100, b=100)
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)