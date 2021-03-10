# TMSpec language

A data flow specification for threat modeling declares the following: components, trust zones, and data flows.
All of these can have properties. For example, you can define a web server component and specify that it implements authentication
and session management, or you can define a data flow and specify that it is encrypted, or transfers personally identifiable information.

TMSpec offers a very powerful way to specify your data flow threat models, borrowing concepts from types and inheritance as used in many programming languages.
This means that you don't have to specify common properties all the time, but you can create a type (e.g. `encrypted_connection`) having the common properties,
and then declare elements of that type.

## version

```
version 0.0;
```

This indicates the version of the TmSpec language. This document explains the
meaning and how to use the language. For the precise syntax, see the
ANTLR4 grammar file.



## zones

```
zone inside;
zone outside: default;
```

Every component must belong to a trust zone. Zones can have properties.
The following properties have a special meaning:

* `default`: when drawing the diagram, don't draw a box around this zone.


## components

```
component customer_webserver(process): zone=inside, cookies, 'sessions::server'=yes;
```

For a component, put the type in parentheses following the components name. The `zone`
property must be present, other attributes are optional. The `zone` property is given
a value, while the `cookies` property is not. If you do not specify an property value,
it will have the Python value `True`. The property `sessions::server` contains
characters not allowed in simple identifiers and therefore needs single quotes around
it.

XXX The Prolog rules do not work well with such properties, it is best to give them an
explicit value.

## data flows

```
flow f1: user --> browser: encryption=false;
flow r1: user <-- browser: encryption=false;

type https(dataflow): encryption=true, authenticated=true;

flow f5(https): client_browser --> customer_webserver, 'format::XML'=yes;
flow r5(https): client_browser <-- customer_webserver, 'privacy::PII'=yes;
```

Dataflows can have a type, but you can also leave it out to give it the default
`dataflow` type. The arrow (left-to-right or right-to-left) indicates the
direction of the flow.


## types

```
type logfile(datastore): is_file=yes, logging=yes;
```

Types can save a lot of property declarations. Simply declare them in the type
definition and then declare a component of that type:

```
component systemlog(logfile): zone=sysadmins;
component eventlog(logfile): zone=auditors;
```


## include

With `include`, you can include other TMSpec files.

XXX not implemented

