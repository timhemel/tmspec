# TMSpec rules

You can specify analysis rules in Prolog. Because Prolog is a complete programming language, you can make very powerful analysis rules.
TMSpec uses the [yldprolog](https://www.github.com/timhemel/yldprolog) library to parse and evaluate the rules.
Prolog is not hard to learn, and for most rules, you will need only very basic Prolog. There are many good tutorials online.

After reading the model specification,
TMSpec will convert the annotated data flow diagram to a set of very basic Prolog clauses. You can build rules on top of these, but the file
`base.prolog` contains some helper Prolog code to make writing rules easier. TMSpec then queries the clauses, specifically it tries to
match `error` and `threat` clauses.


## Defining `error` rules

To define an error, define a clause `error_descr` for the short and long description of the error and `error` to tell TMSpec when this error occurs.

### error_descr

```
error_descr([LIBRARY, ID, VERSION], SHORT_DESCR, LONG_DESCR).
```

Defines an error from the library `LIBRARY` named `ID` (both strings) with version `VERSION` (a positive integer).
Version management of rules can be useful when maintaining a library of rules.

```
error([LIBRARY, ID, VERSION], [V1, ...]) :- clauses.
```

This states that the error rule from the library `LIBRARY`, named `ID` with version `VERSION` (see `error_descr` for an explanation) will remember the
variables `V1, ...` from the clauses and can use these in the short and long description when reporting the error.

The example below defines a rule that will report an error whenever an external entity has any property (`externalentity` is from `base.prolog` and `property` is defined by TMSpec).

```
% Example error: external entities cannot have properties
error_descr(['examples', 'ERR-001', 0], 'Example error in $v1', 'This rule reports an error (in $v1).').
error(['examples', 'ERR-001', 0], [X]) :- externalentity(X), property(X,_,_).
```

## Defining `threat` rules

To define a threat, define a clause `threat_descr` for the short and long description of the threat and `threat` to tell TMSpec when this threat occurs.

### threat_descr

```
threat_descr([LIBRARY, ID, VERSION], SHORT_DESCR, LONG_DESCR).
```

Defines a threat from the library `LIBRARY` named `ID` (both strings) with version `VERSION` (a positive integer).
Version management of rules can be useful when maintaining a library of rules.

```
threat([LIBRARY, ID, VERSION], [V1, ...]) :- clauses.
```

This states that the threat rule from the library `LIBRARY`, named `ID` with version `VERSION` (see `threat_descr` for an explanation) will remember the
variables `V1, ...` from the clauses and can use these in the short and long description when reporting the threat. The description can use `$vn`, where
`n` is a number, for the `n`-th variable in the variable list (starting at 1).

The example below defines a rule that will report a threat whenever a data flow is not encrypted (`dataflow` is from `base.prolog` and `property` is defined by TMSpec).

```
% Example threat: data flow is not encrypted
threat_descr(['examples', 'THR-001', 0], 'Example threat on data flow $v1', 'Data flow from $v2 to $v3 is not encrypted.').
threat(['examples', 'THR-001', 0], [F,X1,X2]) :- dataflow(F,X1,X2)), property(F,encryption,no).
```



## Prolog clauses created by TMSpec

### element

```
element(NAME, TYPE).
```

means that element named `NAME` has type `TYPE`.  
For example, `element(X, datastore)` will find match all datastore elements.

### type

```
type(NAME, TMTYPE)
```

means that there is a type named `NAME`, and is internally represented by the `TmType` Python object `TMTYPE`. It is unlikely that you
will ever need this clause in a rule.

### subtype

```
subtype(CHILD, PARENT)
```

means that type `CHILD` is a direct subtype of type `PARENT`. `CHILD` and `PARENT` are both `TmType` Python objects.

### flow

```
flow(F,C1,C2).
```

means that flow `F` runs from `C1` to `C2`.


### property

```
property(ELEMENT, KEY, VALUE)
```

means that `ELEMENT` has a property named `KEY` and value `VALUE`.

A component's zone is stored as a property of the component.


## Prolog clauses in `base.prolog`

The file `base.prolog` defines several clauses that help you to make rules. See the
comments in its source code for the documentation.


