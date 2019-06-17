from graphviz import Digraph

class GraphvizDFDRenderer:

    def __init__(self, model):
        self.model = model

    def get_dot(self):
        g = self._render()
        return g.view()

    def _get_graphviz_attributes(self, element):
        gv_attrs = [ (a[3:], v) for a,v in element.get_attributes().items()
                    if a.startswith('gv_') ]
        return dict(gv_attrs)

    def _render(self):
        g = Digraph('G', engine='dot', graph_attr={
                'fontname': 'Sans',
                'fontsize': '8',
                'rankdir': 'LR',
            }, node_attr={
                'fontname': 'Sans',
            }, edge_attr={
                'fontname': 'Sans',
                'fontsize': '8',
            })
        for z in self.model.zones:
            zone_components = [ v for c,v in self.model.components.items()
                    if v.get_attr('zone') == z ]
            cluster_attrs = {
                'color': 'red',
                'style': 'dashed',
                'fontcolor': 'red',
                'labelloc': 't',
                'labeljust': 'r',
                'overlap': 'scale',
            }
            with g.subgraph(name='cluster_'+z.name, graph_attr=cluster_attrs) as cluster:
                cluster.attr(label=z.name)
                for c in zone_components:
                    node_attrs = self._get_graphviz_attributes(c)
                    cluster.node(c.name, label=c.name, _attributes=node_attrs)
        for f,v in self.model.flows.items():
            edge_attrs = self._get_graphviz_attributes(v)
            try:
                label = v.get_attr('label')
            except KeyError:
                label = None
            g.edge(v.source.name, v.target.name, label=label, _attributes=edge_attrs)
        return g

