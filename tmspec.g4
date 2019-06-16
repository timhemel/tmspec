grammar tmspec;

start: declaration*;

declaration: component
   | flow
   | zone
   | typedef
   | include
   | versiondef
   ;

component: 'component' name_and_type ':' attributes? ';' ;
name_and_type: identifier typing ;
attributes: attribute ( ',' attribute )*;
attribute: identifier ( '=' value )? ;
typedef: 'type' name_and_type ':' attributes? ';' ;
zone: 'zone' identifier ';' ;
versiondef: 'version' VERSION ';' ;
include: 'include' QSTRING ';' ;
flow: 'flow' identifier typing?':' identifier arrow identifier ',' attributes? ';' ;
arrow: RARROW | LARROW ;
typing: '(' identifier (',' identifier)* ')' ;
value:  boolean | number | identifier | QSTRING ;

boolean: 'true' | 'false' ;
number: NUMBER;

identifier : 'zone' | 'type' | 'flow' | 'include' | 'version' | 'component' | ID ;

NUMBER: DIGIT+ ;
ID : ('A'..'Z'|'a'..'z'|'_'|'0'..'9'|'@')+ ;
VERSION: NUMBER '.' NUMBER ;
QSTRING: '\'' ( ~'\'' | '\\' '\'' )* '\'';
RARROW: '-->';
LARROW: '<--';

fragment DIGIT : [0-9] ;

WS : [ \t\r\n] -> skip ;

