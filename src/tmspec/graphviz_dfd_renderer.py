from graphviz import Digraph
from .TmspecModel import *

class GraphvizDFDRenderer:

    def __init__(self, model):
        self.model = model

    def get_dot(self):
        g = self._render()
        return g.view()

    def _get_graphviz_attributes(self, element):
        gv_attrs = [(a[3:], v) for a, v in element.get_attributes().items()
                        if a.startswith('gv_')]
        return dict(gv_attrs)

    def _create_graph(self):
        g = Digraph('G', engine='dot', graph_attr={
            'fontname': 'Sans',
            'fontsize': '8',
            'rankdir': 'LR',
            'splines': 'spline',
            'size': '7.5,10',
            'ratio': 'fill',
        }, node_attr={
            'fontname': 'Sans',
            'fontsize': '12',
        }, edge_attr={
            'fontname': 'Sans',
            'fontsize': '8',
        })

        return g

    def _render(self):
        graph = self._create_graph()

        self._render_zones_for_zone(graph, None)

        for v in self.model.get_flows():
            edge_attrs = self._get_graphviz_attributes(v)
            try:
                label = v.get_attr('label')
            except KeyError:
                label = None
            
            if defined_before(v.source, v.target):
                graph.edge(v.source.name, v.target.name, label=label, _attributes=edge_attrs)
            else:
                graph.edge(v.target.name, v.source.name, label=label, dir='back', _attributes=edge_attrs)
        return graph

    def _render_zones_for_zone(self, graph, zone):
        for z in self.model.get_zones():
            if z.get_attributes().get('zone') != zone:
                continue

            if z is None:
                zname = '???'
                cluster_attrs = {
                    'color': 'red',
                    'style': 'dashed',
                    'fontcolor': 'red',
                    'labelloc': 't',
                    'labeljust': 'r',
                    'label': zname,
                }
            else:
                zname = z.name
                if z.get_attr('default'):
                    # print('default zone', z.get_attr('default'))
                    cluster_attrs = {
                        'style': 'invis',
                    }
                else:
                    cluster_attrs = {
                        'color': 'red',
                        'style': 'dashed',
                        'fontcolor': 'red',
                        'labelloc': 't',
                        'labeljust': 'r',
                        'label': zname,
                    }

            with graph.subgraph(name='cluster_'+zname, graph_attr=cluster_attrs) as cluster:
                zone_components = self.model.get_zone_components(z)
                for c in zone_components:
                    node_attrs = self._get_graphviz_attributes(c)
                    cluster.node(c.name, label=c.name, _attributes=node_attrs)

                self._render_zones_for_zone(cluster, z)


