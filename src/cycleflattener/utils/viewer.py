import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plotly_data_and_cycle(filt, cycles_with_annot):
    # cycles_with_annot is a pair (cycles, annots) of:
    #   cycles: a list of cycles (each cycle is dict {simplexindex:coeff})
    #   annots: a list of string annotations to label the selector.


    data = pd.DataFrame(filt.vertex_coordinates, columns=["x", "y", "z"])
    print(data.shape)
    print(data.columns)


    # ********** plot (L) **********
    plot_d = dash.dcc.Graph(figure={}, id="3dGraph",
                            style={"height": "80vh"},
                            responsive=True)

    # ********** selector (R1) **********
    cycles, annots = cycles_with_annot
    options = [{"label": f"{i} {annot}", "value": i} for i, annot in enumerate(annots)]
    cycle_selector_d = dash.dcc.Dropdown(options, 0, id='cycle-selector-dropdown', multi=True,
                                         style={"width":"80%"})

    filtration_value_d = dash.html.Div(dash.dcc.Slider(min=0, max=2, step=0.0001,
                                                       value=0, id='filtration-value-slider'),
                                       style={"width":"80%"})

    # ********** control panel (R) **********
    control_d = dash.html.Div([dash.html.H2('1 cycles selected:', id='cycle-selector-title'),
                               cycle_selector_d,
                               dash.html.Br(),
                               dash.html.H2('Filtration Value:'),
                               filtration_value_d,
                               dash.html.Div("hellO", id='dd-output-container')])


    app = dash.Dash()
    app.layout = dash.html.Div([dash.html.H1('Cycle Viewer'),
                                dash.html.Div(children=plot_d,
                                              style={"display":"inline-block", "width":"50%"}),
                                dash.html.Div(children=control_d,
                                              style={"display":"inline-block", "width":"50%",
                                                     "verticalAlign": "top"})])

    # ********** callbacks **********
    @app.callback(
        dash.Output('cycle-selector-title', "children"),
        dash.Input("cycle-selector-dropdown", "value")
    )
    def update_cycle_selection_text(values):
        if type(values) is int:
            num = 1
        else:
            num = len(values)

        return f"{num} cycle{'' if num==1 else 's'} selected:"


    @app.callback(
        dash.Output("3dGraph", "figure"),
        dash.Input("cycle-selector-dropdown", "value"),
        dash.Input("filtration-value-slider", "value"),
        dash.State("3dGraph", "figure")
    )
    def update_graph(b1, b2, old_figure):
        triggered_id = dash.ctx.triggered_id
        print("TRIGGER: ", triggered_id)
        if triggered_id == "cycle-selector-dropdown" or triggered_id is None:
            return update_cycle_selection(b1, old_figure)
        elif triggered_id == "filtration-value-slider":
            return update_filtration_value(b2, old_figure)


    def update_cycle_selection(values, old_figure):
        pointcloud = px.scatter_3d(data, x="x", y="y", z="z", height=1600)
        figdata = pointcloud.data

        def _process(value, figdata):
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
            return figdata

        print("VALUES: ", values)
        if type(values) is int:
            figdata = _process(values,figdata)
        else:
            for value in values:
                figdata = _process(value, figdata)

        figure=go.Figure(data = figdata)
        figure.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        figure.update_traces(marker_size = 2)

        return figure


    def update_filtration_value(value, old_figure):
        return old_figure


    app.run(debug=True)
