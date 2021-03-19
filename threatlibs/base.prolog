%-----------------------------------------------------------------
% isoftype(T1,T2) states that type T1 is a derived type of T2.

isoftype(T,T).
isoftype(T1,T2) :- subtype(T1,T), isoftype(T,T2).


%-----------------------------------------------------------------
% instanceof(X,N) means that X is an element of the type named N.

instanceof(X,N) :- type(N,TP), element(X,T), isoftype(T,TP).


%-----------------------------------------------------------------
% externalentity, process, dataflow, datastore are the four basic
% DFD types. These clauses are convenience clauses to match all
% elements of a basic type (or derived type of it).
%
% A component is anything that is or is derived from any of the
% basic types except dataflow.
%
% component(X) means that X is an external entity, process,
% datastore or anything derived from it.
%
% externalentity(X) means that X is an external entity.
% process(X) means that X is a process.
% datastore(X) means that X is a data store.
% dataflow(X,C1,C2) means that X is a data flow from C1 to C2.

component(X) :- (externalentity(X); process(X); datastore(X)).
externalentity(X) :- instanceof(X,externalentity).
process(X) :- instanceof(X,process).
datastore(X) :- instanceof(X,datastore).
dataflow(X,C1,C2) :- instanceof(X,dataflow), flow(X,C1,C2).

%-----------------------------------------------------------------
% trusted(X,Y) means that X and Y are in the same trust zone.
% untrusted(X,Y) means that X and Y are in a different trust zone.

trusted(X,Y) :- property(X,zone,Z), property(Y,zone,Z).
untrusted(X,Y) :- \+ trusted(X,Y).

%-----------------------------------------------------------------
% member(A,L) means that A is in list L.

member(A,[A|X]) :- !.
member(A,[_|X]) :- member(A,X).

%-----------------------------------------------------------------
% flow_path(L,B) means that the nodes in L form a data flow path
% to B.

flow_path2([A],B,Nodes) :- dataflow(_,A,B), \+ member(A,Nodes).
flow_path2([A,C|X],B,Nodes) :-
	dataflow(_,A,C), \+ member(A,Nodes), flow_path2([C|X],B,[A|Nodes]).
flow_path(L,B) :- flow_path2(L,B,[]).


%-----------------------------------------------------------------
% untrusted_flow_path([A|X],B) means that there is a flow path
% from A to B via the nodes in X, and A and B are in different
% trust zones.
%
% XXX this clause does not detect flow paths that cross a trust
% boundary between nodes in the same trust zone.

untrusted_flow_path([A|X],B) :- flow_path([A|X],B), untrusted(A,B).

%-----------------------------------------------------------------
% all_nodes_type(L,TN) means that all nodes in L are of the type
% named TN.

all_nodes_type([],TN).
all_nodes_type([A|X],TN) :-
	type(TN,TP), element(A,T), isoftype(T,TP), all_nodes_type(X,TN).

%-----------------------------------------------------------------
% all_nodes_prop(L,Prop,Value) means that all nodes in L have
% property Prop set to Value.

all_nodes_prop([],Prop,Value).
all_nodes_prop([A|X],Prop,Value) :-
	property(A,Prop,Value), all_nodes_prop(X,Prop,Value).

%-----------------------------------------------------------------
% all_edges_prop(L,B,Prop,Value) means that all edges of nodes in
% path L ++ [B] have property Prop set to Value.

all_edges_prop([A],B,Prop,Value) :-
	dataflow(F,A,B), property(F,Prop,Value).
all_edges_prop([A,C|X],B,Prop,Value) :-
	dataflow(F,A,C), property(F,Prop,Value),
	all_edges_prop([C|X],Prop,Value).

%-----------------------------------------------------------------
% Model checks
%
% XXX move to separate file?
%

% COMPNOZONE: component without a zone.

error_descr([modelcheck, 'COMPNOZONE', 0], 'component without zone',
   'Component $v1 has no zone.').
error([modelcheck, 'COMPNOZONE', 0], [X]) :-
	component(X),
	\+ property(X,zone,_).

% REFLCONN: component has a data flow to itself.

error_descr([modelcheck, 'REFLCONN', 0], 'data flow to self',
   'An element cannot have a data flow to itself.').
error([modelcheck, 'REFLCONN', 0], [F]) :- dataflow(F,X,X).

% PNOINCFLOW: process has no incoming flow, while it may have an
% outgoing flow (a magic process).

error_descr([modelcheck,'PNOINCFLOW',0],'magic process',
   'Process $v1 cannot magically create data, there must be an incoming flow.').
error([modelcheck,'PNOINCFLOW',0],[X]) :-
	process(X), dataflow(_,X,_), \+ dataflow(_,_,X).

% DNOOUTFLOW: data store has no outgoing flow.

error_descr([modelcheck, 'DNOOUTFLOW', 0], 'data store not read',
   'Data store $v1 only stores data and nothing uses it. You may have missed a component or external entity that reads from $v1.').
error([modelcheck, 'DNOOUTFLOW', 0], [X]) :-
    datastore(X), \+ dataflow(_,X,_).

% DDIRECTFLOW: two data stores communicate directly to each
% other. This requires an process between them.

error_descr([modelcheck, 'DDIRECTFLOW', 0], 'direct data store communication',
   'Data cannot flow between two data stores directly, this requires a process
   (or external entity). Please put a process (or external entity) between
   $v2 and $v3.').
error([modelcheck, 'DDIRECTFLOW', 0], [F,D1,D2]) :-
    datastore(D1), datastore(D2), dataflow(F,D1,D2).

% COMPNOFLOW: component without a data flow.

error_descr([modelcheck, 'COMPNOFLOW', 0], 'component without flow',
	'Component $v1 does not have any incoming or outgoing flows.').
error([modelcheck, 'COMPNOFLOW', 0], [C]) :-
	component(C), \+ flow(_,C,_), \+ flow(_,_,C).

