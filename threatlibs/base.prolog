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

% X and Y have the same trust zone
trusted(X,Y) :- property(X,zone,Z), property(Y,zone,Z).
% X and Y have a different trust zone
untrusted(X,Y) :- \+ trusted(X,Y).

% list membership
member(A,[A|X]) :- !.
member(A,[_|X]) :- member(A,X).

% auxilliary function for flow_path
flow_path2([A],B,Nodes) :- dataflow(_,A,B), \+ member(A,Nodes).
flow_path2([A,C|X],B,Nodes) :-
	dataflow(_,A,C), \+ member(A,Nodes), flow_path2([C|X],B,Nodes).
% there is a flow path following nodes in L ending in B
flow_path(L,B) :- flow_path2(L,B,[]).

% there is a flow path between A and B and A and B have different trust zones
untrusted_flow_path([A|X],B) :- flow_path([A|X],B), untrusted(A,B).

% all nodes in L have type name TN
all_nodes_type([],TN).
all_nodes_type([A|X],TN) :-
	type(TN,TP), element(A,T), isoftype(T,TP), all_nodes_type(X,TN).

% all nodes in L have property Prop set to Value
all_nodes_prop([],Prop,Value).
all_nodes_prop([A|X],Prop,Value) :-
	property(A,Prop,Value), all_nodes_prop(X,Prop,Value).

% all edges of nodes in path L ++ [B] have property Prop set to Value
all_edges_prop([A],B,Prop,Value) :-
	dataflow(F,A,B), property(F,Prop,Value).
all_edges_prop([A,C|X],B,Prop,Value) :-
	dataflow(F,A,C), property(F,Prop,Value),
	all_edges_prop([C|X],Prop,Value).

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
   'Data cannot flow between two data stores directly, this requires a process (or external entity).
Please put a process (or external entity) between $v2 and $v3.') :-
    datastore(D1), datastore(D2), dataflow(F,D1,D2).

