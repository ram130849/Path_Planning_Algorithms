import plotly as ply
from plotly import graph_objs as go

class Plot(object):
    def __init__(self,filename) -> None:
        self.data = []
        self.file_name = './output/visualizations/' + filename + '.html'
        self.layout = {'title': 'Plot',
                       'showlegend': False,
                       'shapes':[]
                       }
        self.fig = {
            'data':self.data,
            'layout': self.layout
        }
    
    def plot_tree(self,trees):
        for tree in trees:
            for start,end in tree.edges.items():
                if end is not None:
                    trace = go.Scatter(
                        x=[start[0], end[0]],
                        y=[start[1], end[1]],
                        line=dict(
                            color='darkblue'
                        ),
                        mode="lines"
                    )
                    self.data.append(trace)
    
    def plot_obstacles(self,obs):
        print(obs)
        for i in range(len(obs)):
            self.layout['shapes'].append({
                        'type': 'rect',
                        'x0': obs[i][0],
                        'y0': obs[i][1],
                        'x1': obs[i][2],
                        'y1': obs[i][3],
                        'line': {
                            'color': 'black',
                            'width': 5,
                        },
                        'fillcolor': 'black',
                        'opacity': 0.60
                    })

    
    def plot_path(self,path):
        x, y = [], []
        for i in path:
            x.append(i[0])
            y.append(i[1])
        trace = go.Scatter(
                x=x,
                y=y,
                line= dict(color="red",width=5),
                mode="lines"
        )
        self.data.append(trace)
    
    def plot(self,x_init,x_end):
        trace = go.Scatter(
                x=[x_init[0]],
                y=[x_init[1]],
                line=dict(
                    color="orange",
                    width=10
                ),
                mode="markers"
            )

        self.data.append(trace)

        trace = go.Scatter(
                x=[x_end[0]],
                y=[x_end[1]],
                line=dict(
                    color="green",
                    width=10
                ),
                mode="markers"
            )

        self.data.append(trace)

    def draw(self, auto_open=True):
        ply.offline.plot(self.fig, filename=self.file_name, auto_open=auto_open)