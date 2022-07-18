import visdcc
import pandas as pd
from dash.dependencies import Input, Output

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc             
from whitenoise import WhiteNoise
from copy import deepcopy

# create app 
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server 
server.wsgi_app = WhiteNoise(server.wsgi_app, root='static/') 

# load data and prune
df = pd.read_csv("data/example.csv")
df = df.query('Omit != 1')
df = df.loc[:, ['Source', 'Target', 'Type', 'Weight', 'Category']]

def generate_data(df):
    node_list = list(set(df['Source'].unique().tolist() + df['Target'].unique().tolist()))
    nodes = [{'id': node_name, 'label': node_name, 'shape': 'dot', 'size': 10} for _, node_name in enumerate(node_list)]

    edges = []
    for row in df.to_dict(orient='records'):
        source, target = row['Source'], row['Target']
        edges.append({
            'id': source + "__" + target,
            'from': source,
            'to': target,
            'width': 2,
        })
    return nodes, edges

nodes, edges = generate_data(df)

ntwk = visdcc.Network(
    id      = 'net', 
    data    = {'nodes'  : nodes,
                'edges'  : edges},
    options = {'height' : '800px', 
                'width'  : '100%',
                'color'  : 'Green'})
app.layout = html.Div([
    ntwk,
    dcc.RadioItems(id       = 'category',
                   options  = [{'label': x, 'value': x} for x in set(df.Category.unique()).union({'All'})], 
                   value    = 'All')          
])

# define callback
@app.callback(Output('net', 'data'), [Input('category', 'value')])
def category_callback(x):
    if x == 'All':
        nodes, edges = generate_data(df)
        return {'nodes'  : nodes,
                'edges'  : edges}
    df_adj = deepcopy(df)
    df_adj = df_adj.query('Category == "{}"'.format(x))
    nodes, edges = generate_data(df_adj)
    return {'nodes'  : nodes,
            'edges'  : edges}

# define main calling
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)