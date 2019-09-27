% isoftype(T1,T2)
%
% States that type T1 is a derived type of T2.
isoftype(T,T).
isoftype(T1,T2) :- subtype(T1,T), isoftype(T,T2).

% externalentity, process, dataflow, datastore
externalentity(X) :- type(externalentity,TP), element(X,T), isoftype(T,TP).
process(X) :- type(process,TP), element(X,T), isoftype(T,TP).
dataflow(X) :- type(dataflow,TF), element(X,T), isoftype(T,TF).
datastore(X) :- type(datastore,TF), element(X,T), isoftype(T,TF).

