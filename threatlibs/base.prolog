% isoftype(T1,T2)
%
% States that type T1 is a derived type of T2.

isoftype(T,T).
isoftype(T1,T2) :- subtype(T1,T), isoftype(T,T2).

% externalentity, process, dataflow, datastore

externalentity(X) :- type(externalentity,TP), element(X,T), isoftype(T,TP).
process(X) :- type(process,TP), element(X,T), isoftype(T,TP).
datastore(X) :- type(datastore,TF), element(X,T), isoftype(T,TF).
dataflow(X,C1,C2) :-
	type(dataflow,TF), element(X,T), isoftype(T,TF), flow(X,C1,C2).

% model checks

error([modelcheck, REFLCONN, 0], [F], 'data flow to self',
   'An element cannot have a data flow to itself.') :- dataflow(F,X,X).

error([modelcheck,PNOINCFLOW,0],[X],'magic process',
   'Processes do not magically create data, there must be an incoming flow.') :-
   process(X), \+ dataflow(_,_,X).

error([modelcheck, DNOOUTFLOW, 0], [X], 'data store not read',
   'Data store $v1 only stores data, which is pointless. You may have missed a component or external entity that reads from $v1.') :-
    datastore(X), \+ dataflow(_,X,_).

error([modelcheck, DDIRECTFLOW, 0], [F,D1,D2], 'direct data store communication',
   'Data cannot flow between two data stores directly, this requires a process.
Please put a process between $v2 and $v3.') :-
    datastore(D1), datastore(D2), dataflow(F,D1,D2).

