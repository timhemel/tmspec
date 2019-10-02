threat_descr(['test', '001', 0], 'Test threat', 'This is a threat to test').
threat(['test', '001', 0], [X]) :-
     process(X), property(X,'authentication::login',yes).
% any flow is a threat
threat_descr(['test', '002', 0], 'threat to $v1', 'One more threat (on $v1).').
threat(['test', '002', 0], [X]) :- dataflow(X).
% any externalentity is an error
error_descr(['test', '001', 0], 'error in $v1', 'One more error (in $v1).').
error(['test', '001', 0], [X]) :- externalentity(X).


