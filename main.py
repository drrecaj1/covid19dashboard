import dash
from utils import (
    get_data,
    get_date_time_values,
    get_counties_for_a_state,
    organize_data_for_a_state,
    organize_data_for_all_states,
)
from plotly import express as px
from datetime import datetime


app = dash.Dash(__name__)  # initialising dash app

raw_data = get_data()
default_state = "California"
all_time_values, length = get_date_time_values(raw_data=raw_data)

app.layout = dash.html.Div(
    [
        dash.html.Div(
            [
                dash.html.H4("Covid cases confirmed per State in USA"),
                dash.dcc.Graph(id="time-series-chart"),
                dash.dcc.Loading(
                    id="loading",
                    type="default",
                    children=dash.html.Div(id="loading-output"),
                ),
                dash.html.P("Select state:"),
                dash.dcc.Dropdown(
                    id="states",
                    options=raw_data["Province_State"].unique(),
                    value=default_state,
                ),
                dash.html.P("Select counties:"),
                dash.dcc.Dropdown(
                    id="counties",
                    options=get_counties_for_a_state(
                        us_state=default_state,
                        raw_data=raw_data,
                    ),
                    value=None,
                    multi=True,
                    clearable=True,
                ),
                dash.html.Div(
                    [
                        dash.html.Div(
                            [
                                dash.html.P("From time: "),
                                dash.dcc.Dropdown(
                                    id="from_time",
                                    options=all_time_values,
                                    value=0,
                                ),
                            ],
                            style={
                                "width": "48%",
                                "display": "inline-block",
                            },
                        ),
                        dash.html.Div(
                            [
                                dash.html.P("To time:"),
                                dash.dcc.Dropdown(
                                    id="to_time",
                                    options=all_time_values,
                                    value=length - 1,
                                ),
                            ],
                            style={
                                "width": "48%",
                                "display": "inline-block",
                            },
                        ),
                    ]
                ),
            ]
        ),
        dash.html.Div(
            [
                dash.html.H4("Covid cases confirmed in USA"),
                dash.dcc.Graph(id="time-series-chart-for-all"),
                dash.dcc.Loading(
                    id="loading2",
                    type="default",
                    children=dash.html.Div(id="loading-output2"),
                ),
                dash.html.Div(
                    [
                        dash.html.Div(
                            [
                                dash.html.P("From time: "),
                                dash.dcc.Dropdown(
                                    id="from_time2",
                                    options=all_time_values,
                                    value=0,
                                ),
                            ],
                            style={
                                "width": "48%",
                                "display": "inline-block",
                            },
                        ),
                        dash.html.Div(
                            [
                                dash.html.P("To time:"),
                                dash.dcc.Dropdown(
                                    id="to_time2",
                                    options=all_time_values,
                                    value=length - 1,
                                ),
                            ],
                            style={
                                "width": "48%",
                                "display": "inline-block",
                            },
                        ),
                    ]
                ),
            ]
        ),
    ]
)


@app.callback(
    dash.Output(component_id="counties", component_property="options"),
    dash.Input(component_id="states", component_property="value"),
)
def update_counties_select(selected_state):
    return get_counties_for_a_state(raw_data=raw_data, us_state=selected_state)


@app.callback(
    [
        dash.Output(
            component_id="time-series-chart",
            component_property="figure",
        ),
        dash.Output(
            component_id="loading-output",
            component_property="children",
        ),
    ],
    dash.Input(component_id="states", component_property="value"),
    dash.Input(component_id="counties", component_property="value"),
    dash.Input(component_id="from_time", component_property="value"),
    dash.Input(component_id="to_time", component_property="value"),
)
def update_graph(
    selected_state,
    selected_counties,
    selected_from_time,
    selected_to_time,
):
    if int(selected_from_time) >= int(selected_to_time):
        return dash.no_update, "Not valid time range period."
    from_time = datetime.strptime(
        all_time_values[int(selected_from_time)],
        "%d %b, %Y",
    )
    to_time = datetime.strptime(
        all_time_values[int(selected_to_time)],
        "%d %b, %Y",
    )

    raw = get_data()
    counties = get_counties_for_a_state(raw_data=raw, us_state=selected_state,)
    if selected_counties and not all(county in counties for county in selected_counties):
        selected_counties = None

    df = organize_data_for_a_state(
        raw_data=raw,
        us_state=selected_state,
        counties=selected_counties,
        from_time=from_time,
        to_time=to_time,
    )
    fig = px.line(df)
    fig.update_layout(
        title=f"Covid19 confirmed cases for {selected_state}",
        xaxis_title="Time",
        yaxis_title="Number of cases",
        legend_title="Counties",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple",
        ),
    )

    return fig, True


@app.callback(
    [
        dash.Output(
            component_id="time-series-chart-for-all",
            component_property="figure",
        ),
        dash.Output(
            component_id="loading-output2",
            component_property="children",
        ),
    ],
    dash.Input(component_id="from_time2", component_property="value"),
    dash.Input(component_id="to_time2", component_property="value"),
)
def update_graph_for_all_states(selected_from_time, selected_to_time):
    if int(selected_from_time) >= int(selected_to_time):
        return dash.no_update, "Not valid time range period."
    from_time_str = all_time_values[int(selected_from_time)]
    from_time = datetime.strptime(
        from_time_str,
        "%d %b, %Y",
    )
    to_time_str = all_time_values[int(selected_to_time)]
    to_time = datetime.strptime(
        to_time_str,
        "%d %b, %Y",
    )
    raw = get_data()
    df = organize_data_for_all_states(
        raw_data=raw,
        from_time=from_time,
        to_time=to_time,
    )
    fig = px.line(df)
    fig.update_layout(
        title=f"Covid19 confirmed cases for all states ({from_time_str} - {to_time_str})",
        xaxis_title="Time",
        yaxis_title="Number of cases",
        legend_title="States",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="RebeccaPurple",
        ),
    )
    return fig, True

server = app.server
