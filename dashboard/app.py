import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import wordninja

df = pd.read_csv('shap_values.csv')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Impact of YouTube Video Content on Engagement", style={'textAlign': 'center'}),
    html.P("""In this project, we joined content features form YouTube8m with viewcounts for YouTube videos. 
           We fit predictive models for each year, an extracted feature importance (SHAP values, units of view count
            percentile for the year) for the content features. Using this, we can examine how the impact of video 
           contents on engagement changes over time.
           """, style={'padding': '0px 20px 0px 20px'}),
    html.P("""You can view the impact of an individual feature over time in the line chart below.  The orange region 
           indicates the topic negatively predicted engagement. The blue region shows a positive impact on engagement.
           Alternatively, expand the box plot and select the year of interest to see how feature impacts stack up 
           comparatively. Clicking a feature in the box plot will select it in the line chart.
           """, style={'padding': '0px 20px 0px 20px'}),

    dbc.Collapse(
        id='linegraph-collapse',
        is_open=True,
        children=[
            html.Div([
                html.Label("Select Category:"),
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[
                        {'label': " ".join([word for word in wordninja.split(var)]), 'value': var}
                        for var in sorted(df['variable'].unique())
                    ],
                    value=df['variable'].unique()[0],
                    style={'width': '200px'}
                )
            ], style={'margin': '20px'}),
            dcc.Graph(id='line-graph', style={'height': '600px'})
        ]
    ),
        html.Button("View Box Plot for Feature Importance by year", id="toggle-boxplot-button", n_clicks=0, style={'margin': '20px'}),
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
            dcc.Graph(id='shap-boxplot', style={'height': '2048px'})
        ]
    ),

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
    Output('shap-boxplot', 'figure'),
    Input('year-dropdown', 'value')
)
def update_boxplot(selected_year):
    filtered_df = df[df['year'] == selected_year]
    filtered_df = filtered_df[~filtered_df['variable'].str.startswith('posted_day_')]
    filtered_df['variable'] = filtered_df['variable'].apply(
        lambda x: " ".join([word for word in wordninja.split(x)])
    )
    variables = filtered_df.groupby('variable')['value'].mean().sort_values(ascending=False).index.tolist()
    fig = go.Figure()
    variables_to_display = []
    for variable in variables:
        var_data = filtered_df[filtered_df['variable'] == variable]['value']
        if len(var_data) > 0:
            variables_to_display.append(variable)
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
                hoverinfo='skip',
                boxpoints=False # remove outliers for more legibility
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
        height=2048,
        margin=dict(l=150, r=50, t=100, b=100),
        
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
        name=selected_category,
        marker=dict(color="black")
    ))
    boundary = max(abs(min(mean_shap['value'])), abs(max(mean_shap['value'])))*1.1
    fig.update_yaxes(range=[-1*boundary, boundary])
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, x1=1, y0=0, y1=boundary,
        fillcolor="blue",
        opacity=0.3,
        layer="below",
        line_width=0,
    )
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, x1=1, y0=-1*boundary, y1=0,
        fillcolor="orange",
        opacity=0.3,
        layer="below",
        line_width=0,
    )
    fig.update_layout(
        title=f"Mean Feature Importance Over Time for {selected_category}",
        xaxis_title="Year",
        yaxis_title="Mean SHAP Value",
        showlegend=False,
        height=600,
        margin=dict(l=50, r=50, t=100, b=100)
    )
    return fig

@app.callback(
    Output('category-dropdown', 'value'),
    Input('shap-boxplot', 'clickData'),
    State('category-dropdown', 'value'),
    prevent_initial_call=True
)
def toggle_dropdown(clickData, current_value):
    if clickData is None:
        # Do nothing on initial load or non-click
        return current_value
    # Toggle selection in line chart.
    clicked_topic = clickData['points'][0]['y'].replace(" ", "") # get the topic name clicked
    return clicked_topic

app.clientside_callback(
    """
    function(n_clicks) {
        // Scroll to the linegraph
        const element = document.getElementById('linegraph-collapse');
        console.log(element);
        element.scrollIntoView({behavior: 'smooth'});
    }
    """,
    Input('shap-boxplot', 'clickData')
)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=80)
