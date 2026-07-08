import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plotly_data_and_cycle(filt, cycles):
    data = pd.DataFrame(filt.vertex_coordinates, columns=["x", "y", "z"])
    print(data.shape)
    print(data.columns)

    app = dash.Dash()
    app.layout = dash.html.Div(children=\
                               [dash.html.H4('Hello World'),
                                dash.html.Div(children=\
                                              dash.dcc.Graph(figure={}, id="3dGraph",style={"height": "80vh"}, responsive=True)),
                                dash.dcc.Dropdown(list(range(len(cycles))), 0, id='cycle-dd-selector'),
                                dash.html.Div(id='dd-output-container')])

    @app.callback(
        dash.Output("3dGraph", "figure"),
        dash.Input("cycle-dd-selector", "value")
    )
    def update_3dGraph(value):
        pointcloud = px.scatter_3d(data, x="x", y="y", z="z", height=1600)
        figdata = pointcloud.data

        if value == 0:
            color = "red"
        else:
            color = "green"


        for simp_cycle in filt.get_1_cycle_vertices(cycles[value]):
            idxs = simp_cycle + [simp_cycle[0]]
            linedata = pd.DataFrame(data.iloc[idxs,:])
            linedata["colors"] = [color] * linedata.shape[0]

            figdata += px.line_3d(linedata, x="x", y="y", z="z",
                                  color="colors", color_discrete_map="identity",
                                  height=1600).data

        figure=go.Figure(data = figdata)
        figure.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        figure.update_traces(marker_size = 2)
        return figure


    app.run(debug=True)
