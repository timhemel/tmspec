#!/bin/bash

GRAMMAR=tmspec
d=`dirname "$0"`


rm -f "$d"/${GRAMMAR}Lexer.py "$d"/${GRAMMAR}Lexer.tokens "$d"/${GRAMMAR}Listener.py "$d"/${GRAMMAR}Parser.py "$d"/${GRAMMAR}.tokens "$d"/${GRAMMAR}Visitor.py

g=`realpath "$d"/${GRAMMAR}.g4`

pushd "$d"
# antlr4 -o "$d" -Dlanguage=Python3 -visitor "$g"
antlr4 -o "$d" -Dlanguage=Python3 -visitor "$GRAMMAR.g4"
popd

