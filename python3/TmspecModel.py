from TmspecError import *

class TmElement:
    def __init__(self, name):
        self.name = name

class TmElementWithAttributes(TmElement):

    def __init__(self, name, input_ctx, parents=[], attrs={}):
        super(TmElementWithAttributes, self).__init__(name)
        self.parents = parents
        self.attr = attrs
        self.input_ctx = input_ctx

    def get_position(self):
        return self.input_ctx.get_position()

    def get_attr(self, key):
        try:
            return self.attr[key]
        except KeyError:
            for p in self.parents:
                try:
                    return p.get_attr(key)
                except KeyError:
                    pass
        raise KeyError(key)

    def get_attributes(self):
        d = {}
        for p in reversed(self.parents):
            d.update(p.get_attributes())
        d.update(self.attr)
        return d

class TmComponent(TmElementWithAttributes):

    def get_types(self):
        return self.parents

class TmType(TmElementWithAttributes):

    def get_base_types(self):
        if self.parents:
            base_types = set([])
            for t in self.parents:
                base_types.update(t.get_base_types())
            return base_types
        return set([self.name])

class TmFlow(TmElementWithAttributes):

    def __init__(self, name, input_ctx, source, target, parents=[], attrs={}):
        super(TmFlow, self).__init__(name, input_ctx, parents, attrs)
        self.source = source
        self.target = target

class TmZone(TmElementWithAttributes):
    def __init__(self, name, input_ctx, attrs={}):
        super(TmZone, self).__init__(name, input_ctx, [], attrs)

def defined_before(e1, e2):
    return e1.get_position() <= e2.get_position()

class TmspecModel:

    def __init__(self):
        self.zones = set([])
        self.components = {}
        self.flows = {}
        self.identifiers = {
            'process' : TmType('process', attrs={
                'gv_shape': 'oval',
            }),
            'datastore' : TmType('datastore', attrs={
                'gv_shape': 'cylinder',
                # SVG image is possible, but must have width and height
                # 'gv_image': '/usr/share/pixmaps/fedora-logo-sprite.svg',
                # html labels are another possibility
            }),
            'dataflow' : TmType('dataflow', attrs={
            }),
            'externalentity' : TmType('externalentity', attrs={
                'gv_shape': 'rect',
            }),
        }
        # self.types = {}

    def has_identifier(self, identifier):
        return identifier in self.identifiers

    def get_identifier(self, identifier):
        return self.identifiers.get(identifier)

    def add_zone(self, zone):
        self.zones.add(zone)
        self.identifiers[zone.name] = zone

    def get_zones(self):
        # TODO: check if we can preserve parse order
        return [ x[1] for x in sorted([ (z.get_position(), z) for z in self.zones ]) ]

    def get_zone_components(self, z):
        return [ x[1] for x in
                sorted([ (v.get_position(), v)
                    for c,v in self.components.items()
                    if v.get_attr('zone') == z ]) ]

    def get_flows(self):
        return [ x[1] for x in 
            sorted([ (v.get_position(), v) for v in self.flows.values() ]) ]


    def add_component(self, component):
        self.components[component.name] = component
        self.identifiers[component.name] = component

    def add_flow(self, flow):
        self.flows[flow.name] = flow
        self.identifiers[flow.name] = flow

    def add_type(self, tm_type):
        # self.types[tm_type.name] = tm_type
        self.identifiers[tm_type.name] = tm_type
