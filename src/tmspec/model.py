from .error import *

import pkg_resources
import os

class TmElement:
    def __init__(self, name):
        self.name = name

class TmElementWithAttributes(TmElement):

    def __init__(self, name, input_ctx, parents=[], attrs={}):
        super(TmElementWithAttributes, self).__init__(name)
        self._parents = parents
        self._attrs = attrs
        self.input_ctx = input_ctx

    @property
    def position(self):
        return self.input_ctx.position

    @property
    def filename(self):
        return self.input_ctx.filename

    def __getitem__(self, key):
        try:
            return self._attrs[key]
        except KeyError:
            for p in self._parents:
                try:
                    return p[key]
                except KeyError:
                    pass
        raise KeyError(key)

    def get(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    @property
    def attributes(self):
        d = {}
        for p in reversed(self._parents):
            d.update(p.attributes)
        d.update(self._attrs)
        return d

    @property
    def types(self):
        return self._parents

class TmComponent(TmElementWithAttributes):

    pass


class TmType(TmElementWithAttributes):

    @property
    def base_types(self):
        if self.types == []:
            return { self.name }
        return set().union( *(t.base_types for t in self.types ))

class TmFlow(TmElementWithAttributes):

    def __init__(self, name, input_ctx, source, target, parents=[], attrs={}):
        super(TmFlow, self).__init__(name, input_ctx, parents, attrs)
        self.source = source
        self.target = target

class TmZone(TmElementWithAttributes):
    def __init__(self, name, input_ctx, attrs={}):
        super(TmZone, self).__init__(name, input_ctx, [], attrs)

def defined_before(e1, e2):
    return e1.position <= e2.position

class TmspecModel:

    def __init__(self):
        self.zones = {}
        self.components = {}
        self.flows = {}
        self.identifiers = {
            'process' : TmType('process', None, attrs={
                'gv_shape': 'oval',
            }),
            'datastore' : TmType('datastore', None, attrs={
                #'gv_shape': 'cylinder',
                'gv_shape': 'none',
                # SVG image is possible, but must have width and height
                'gv_image': pkg_resources.resource_filename('tmspec', os.path.join('resources', 'datastore.svg')),
                # html labels are another possibility
            }),
            'dataflow' : TmType('dataflow', None, attrs={
            }),
            'externalentity' : TmType('externalentity', None, attrs={
                'gv_shape': 'rect',
            }),
        }
        self.types = self.identifiers.copy()

    def has_identifier(self, identifier):
        return identifier in self.identifiers

    def get_identifier(self, identifier):
        return self.identifiers.get(identifier)

    def get_types(self):
        """return all types, not sorted in any particular order."""
        return self.types.values()

    def get_zones(self):
        """return all zones, sorted by their position in the spec file."""
        return [ x[1] for x in sorted([ (z.position, z) for z in self.zones.values() ]) ]

    def get_zone_components(self, z):
        """return all components for zone z, sorted by their position in the spec file.
        If z is None, return the unzoned components."""
        return [ x[1] for x in
                sorted([ (v.position, v)
                    for c,v in self.components.items()
                    if v.get('zone') == z ]) ]

    def get_flows(self):
        """return all data flows, sorted by their position in the spec file."""
        return [ x[1] for x in 
            sorted([ (v.position, v) for v in self.flows.values() ]) ]

    def add_zone(self, zone):
        self.zones[zone.name] = zone
        self.identifiers[zone.name] = zone

    def add_component(self, component):
        self.components[component.name] = component
        self.identifiers[component.name] = component

    def add_flow(self, flow):
        self.flows[flow.name] = flow
        self.identifiers[flow.name] = flow

    def add_type(self, tm_type):
        self.types[tm_type.name] = tm_type
        self.identifiers[tm_type.name] = tm_type
