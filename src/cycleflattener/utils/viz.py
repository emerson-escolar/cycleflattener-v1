import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_data_and_cycle(filt, cycle, color, ofname,
                        set_aspect=False, show=False):
    #  cycle is a dictionary {simplexindex:coeff} representing a cycle.
    data = filt.vertex_coordinates

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(data[:, 0], data[:, 1], data[:, 2], s=1, c="blue")
    for simp_cycle in filt.get_1_cycle_vertices(cycle):
        idxs = simp_cycle + [simp_cycle[0]]
        ax.plot(data[idxs, 0], data[idxs, 1], data[idxs, 2], c=color)
    if set_aspect:
        ax.set_box_aspect((np.ptp(data[:,0]), np.ptp(data[:,1]), np.ptp(data[:,2])))

    plt.savefig(ofname)
    if show:
        plt.show(block=True)




def plotly_data_and_cycle(filt, cycles_with_annot, max_filtration_value):
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

    # ********** filtration value slider (R2) **********
    filtration_value_d = dash.html.Div(dash.dcc.Slider(min=0, max=max_filtration_value, step=0.0001,
                                                       value=0, id='filtration-value-slider'),
                                       style={"width":"80%"})

    # ********** control panel (R) **********
    control_d = dash.html.Div([dash.html.H2('1 cycles selected:', id='cycle-selector-title'),
                               cycle_selector_d,
                               dash.html.Br(),
                               dash.html.H2('Filtration Value:', id="filtration-value-title"),
                               filtration_value_d,
                               dash.html.Br(),
                               dash.html.Div("Warning: only triangles displayed.", id='dd-output-container')])


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
        dash.Output('filtration-value-title', "children"),
        dash.Input("filtration-value-slider", "value")
    )
    def update_filtration_value_text(value):
        return f"Filtration value {value} selected:"


    @app.callback(
        dash.Output("3dGraph", "figure"),
        dash.Input("cycle-selector-dropdown", "value"),
        dash.Input("filtration-value-slider", "value"),
        dash.State("3dGraph", "figure")
    )
    def update_graph(select_v, filt_v, old_figure):
        pointcloud = px.scatter_3d(data, x="x", y="y", z="z", height=1600)
        figdata = pointcloud.data

        def _process(value, figdata):
            print("figdata type:", type(figdata))
            if value == 0:
                color = "red"
            else:
                color = "blue"
            for simp_cycle in filt.get_1_cycle_vertices(cycles[value]):
                idxs = simp_cycle + [simp_cycle[0]]
                linedata = pd.DataFrame(data.iloc[idxs,:])
                linedata["colors"] = [color] * linedata.shape[0]

                figdata += px.line_3d(linedata, x="x", y="y", z="z",
                                      color="colors", color_discrete_map="identity",

                                      height=1600).data
                print("added object of type:", type(figdata[-1]))
            return figdata

        print("VALUES: ", select_v)
        if type(select_v) is int:
            figdata = _process(select_v,figdata)
        else:
            for value in select_v:
                figdata = _process(value, figdata)

        figure=go.Figure(data = figdata)
        figure.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        figure.update_traces(marker_size = 2)
        figure.update_traces(line=dict(width=8))

        triangles = np.array(filt.context_triangles(filt_v))
        print(triangles.shape)
        if len(triangles) == 0:
            return figure

        figure.add_mesh3d(x=data.loc[:,"x"],
                          y=data.loc[:,"y"],
                          z=data.loc[:,"z"],
                          i=triangles[:,0],
                          j=triangles[:,1],
                          k=triangles[:,2],
                          opacity=0.5, color="yellow")

        return figure



    app.run(debug=True)
