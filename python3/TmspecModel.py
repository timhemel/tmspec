from TmspecError import *

class TmElement:
    def __init__(self, name):
        self.name = name

class TmElementWithAttributes(TmElement):

    def __init__(self, name, parents=[], attrs={}):
        super(TmElementWithAttributes, self).__init__(name)
        self.parents = parents
        self.attr = attrs

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

    def __init__(self, name, source, target, parents=[], attrs={}):
        super(TmFlow, self).__init__(name, parents, attrs)
        self.source = source
        self.target = target

class TmZone(TmElementWithAttributes):
    def __init__(self, name, attrs={}):
        super(TmZone, self).__init__(name, [], attrs)

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

    def add_component(self, component):
        self.components[component.name] = component
        self.identifiers[component.name] = component

    def add_flow(self, flow):
        self.flows[flow.name] = flow
        self.identifiers[flow.name] = flow

    def add_type(self, tm_type):
        # self.types[tm_type.name] = tm_type
        self.identifiers[tm_type.name] = tm_type
