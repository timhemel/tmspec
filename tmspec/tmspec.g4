grammar tmspec;

start: versiondef declaration* EOF;

declaration: component
   | flow
   | zone
   | typedef
   | include
   ;

component: 'component' name_and_type ( ':' attributes )? ';' ;
name_and_type: identifier typing ;
attributes: attribute ( ',' attribute )*;
attribute: (identifier|QSTRING) ( '=' value )? ;
typedef: 'type' name_and_type ( ':' attributes )? ';' ;
zone: 'zone' identifier ( ':' attributes )? ';' ;
versiondef: 'version' VERSION ';' ;
include: 'include' QSTRING ';' ;
flow: 'flow' identifier typing?':' identifier arrow identifier (',' attributes)? ';' ;
arrow: RARROW | LARROW ;
typing: '(' identifier (',' identifier)* ')' ;
value:  boolean | number | identifier | QSTRING ;

boolean: 'true' | 'false' ;
number: NUMBER;

identifier : 'zone' | 'type' | 'flow' | 'include' | 'version' | 'component' | ID ;

NUMBER: DIGIT+ ;
ID : ('A'..'Z'|'a'..'z'|'_'|'0'..'9'|'@')+ ;
VERSION: NUMBER '.' NUMBER ;
QSTRING: '\'' ( ESC | ~['\\] )* '\'';
RARROW: '-->';
LARROW: '<--';

fragment DIGIT : [0-9] ;
fragment ESC : '\\' (['\\bfnrt] | UNICODE);
fragment UNICODE : 'u' HEX HEX HEX HEX;
fragment HEX : [0-9a-fA-F] ;


WS : [ \t\r\n] -> skip ;
LINE_COMMENT: ('#'|'//') .*? '\n' -> skip ;
COMMENT: '/*' .*? '*/' -> skip ;

