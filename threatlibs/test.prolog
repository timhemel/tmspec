threat(['test', '001', 0], [X], 'Test threat', 'This is a threat to test')
    :- process(X), property(X,'authentication::login',yes).
% any flow is a threat
threat(['test', '002', 0], [X], 'threat to $v1', 'One more threat (on $v1).')
    :- dataflow(X).
% any externalentity is an error
error(['test', '001', 0], [X], 'error in $v1', 'One more error (in $v1).')
    :- externalentity(X).


