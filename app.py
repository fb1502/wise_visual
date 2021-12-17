import re
import pandas as pd
import get_statements as gs
import get_map as gm
import flatten_dict as fd
from datetime import date, datetime, timedelta, timezone

import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
from dash.exceptions import PreventUpdate

# map
import plotly.graph_objects as go

# getting statement and transactions
statement = gs.get_statement()

if statement is not None:
    df = pd.DataFrame.from_dict([fd.stringify_flatten_dict(fd.flatten_dict(x)) for x in statement['transactions']])
    df['details_merchant_city'] = df['details_merchant_city'].str.upper()

app = dash.Dash(__name__)

app.layout = html.Div(
    [
    # dash_table.DataTable(
    #     id='my-table',
    #     page_size = 10,
    #     sort_action='native',
    #     columns=
    #     [
    #         {
    #         "name": i,
    #         "id": i,
    #         "deletable": True,
    #         }
    #         for i in df.columns
    #     ],
    #     # data=df.to_dict('records'),
    # ),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(1995, 8, 5),
        max_date_allowed=date.today(),
        initial_visible_month=date.today(),
        start_date=date.today() - timedelta(days=10),
        end_date=date.today()
    ),
    html.Div(id='output-container-date-picker-range'),
    html.Br(),
    html.Div(id='my-output'),
    html.Div(id='my-map'),
    # dcc.Graph(id="pie-chart-category"),
    # dcc.Graph(id="pie-chart-city"),
    # dcc.Graph(id="pie-chart-country"),
])

@app.callback(
    [
    # Output('my-table', 'data'),
    Output('my-output', 'children'),
    # Output("pie-chart-category", "figure"), 
    # Output("pie-chart-city", "figure"), 
    # Output("pie-chart-country", "figure"), 
    Output("my-map", "children"), 
    Output('my-date-picker-range', "initial_visible_month"),
    ],
    [
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    ], prevent_initial_call=True
    )

def update_output_div(start_date, end_date):
    # Determining which Input has fired, prevent update when 'start_date' changed
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'my-date-picker-range.start_date':
        raise PreventUpdate

    end_date_record = end_date

    start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc).isoformat()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc).isoformat()

    statement = gs.get_statement(interval_start = start_date, interval_end = end_date)

    if statement is not None:
        df = pd.DataFrame.from_dict([fd.stringify_flatten_dict(fd.flatten_dict(x)) for x in statement['transactions']])
        df['details_merchant_city'] = df['details_merchant_city'].str.upper() 

    table_data = df.to_dict('records')
    output_str = 'Total used EUR: {}'.format(round(df[df.amount_value<0].amount_value.sum(),2))

    df2 = df[df.amount_value<0].copy()
    df2.amount_value = df2.amount_value.abs()

    addr_df = (df2.details_merchant_name + ', ' + df2.details_merchant_city).value_counts().to_frame(name='count')

    lat = []
    lng = []
    for index, row in addr_df.iterrows():
        geo_json = gm.google_find_place(index)
        if len(geo_json['candidates']) == 0:
            lat.append(None)
            lng.append(None)
        else:
            lat.append(geo_json['candidates'][0]['geometry']['location']['lat'])
            lng.append(geo_json['candidates'][0]['geometry']['location']['lng'])
    addr_df['lat'] = lat
    addr_df['lng'] = lng

    fig_category = px.pie(df2, values='amount_value', names='details_category')
    fig_city = px.pie(df2, values='amount_value', names='details_merchant_city')
    fig_country = px.pie(df2, values='amount_value', names='details_merchant_country')

    fig = go.Figure(go.Densitymapbox(lat=addr_df['lat'], lon=addr_df['lng'], z=addr_df['count'],
                                     radius=50))
    fig.update_layout(mapbox_style="open-street-map", mapbox_center_lon=180)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # return table_data, output_str, fig_category, fig_city, fig_country, dcc.Graph(figure=fig), end_date_record
    return output_str, dcc.Graph(figure=fig), end_date_record

if __name__ == '__main__':
    app.run_server(debug=True)