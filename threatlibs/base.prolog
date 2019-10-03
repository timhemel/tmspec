% isoftype(T1,T2)
%
% States that type T1 is a derived type of T2.

isoftype(T,T).
isoftype(T1,T2) :- subtype(T1,T), isoftype(T,T2).

instanceof(X,N) :- type(N,TP), element(X,T), isoftype(T,TP).

% externalentity, process, dataflow, datastore

externalentity(X) :- instanceof(X,externalentity).
process(X) :- instanceof(X,process).
datastore(X) :- instanceof(X,datastore).
dataflow(X,C1,C2) :- instanceof(X,dataflow), flow(X,C1,C2).

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
	dataflow(_,A,C), \+ member(A,Nodes), flow_path2([C|X],B,[A|Nodes]).
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
error_descr([modelcheck, 'COMPNOZONE', 0], 'component without zone',
   'Component $v1 has no zone.').
error([modelcheck, 'COMPNOZONE', 0], [X]) :-
	(datastore(X); process(X); externalentity(X)),
	\+ property(X,zone,_).

error_descr([modelcheck, 'REFLCONN', 0], 'data flow to self',
   'An element cannot have a data flow to itself.').
error([modelcheck, 'REFLCONN', 0], [F]) :- dataflow(F,X,X).

error_descr([modelcheck,'PNOINCFLOW',0],'magic process',
   'Process $v1 cannot magically create data, there must be an incoming flow.').
error([modelcheck,'PNOINCFLOW',0],[X]) :-
	process(X), dataflow(_,X,_), \+ dataflow(_,_,X).

error_descr([modelcheck, 'DNOOUTFLOW', 0], 'data store not read',
   'Data store $v1 only stores data, which is pointless. You may have missed a component or external entity that reads from $v1.').
error([modelcheck, 'DNOOUTFLOW', 0], [X]) :-
    datastore(X), \+ dataflow(_,X,_).

error_descr([modelcheck, 'DDIRECTFLOW', 0], 'direct data store communication',
   'Data cannot flow between two data stores directly, this requires a process
   (or external entity). Please put a process (or external entity) between
   $v2 and $v3.').
error([modelcheck, 'DDIRECTFLOW', 0], [F,D1,D2]) :-
    datastore(D1), datastore(D2), dataflow(F,D1,D2).

error_descr([modelcheck, 'COMPNOFLOW', 0], 'component without flow',
	'Component $v1 does not have any incoming or outgoing flows.').
error([modelcheck, 'COMPNOFLOW', 0], [C]) :-
	(datastore(C); externalentity(C); process(C)),
	\+ flow(_,C,_), \+ flow(_,_,C).

