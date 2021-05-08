syntax clear
syntax case match


syntax keyword tmspecDirectiveKeyword version include contained skipwhite
syntax region tmspecDirective start=/version\|include/ end=/;/ contains=tmspecDirectiveKeyword,tmspecInlineComment
syntax keyword tmspecDeclarationKeyword zone component type flow contained skipwhite
syntax region tmspecDeclaration start=/\(zone\|component\|type\|flow\)\s*/ end=/;/ contains=tmspecNonflowStatement,tmspecFlowStatement,tmspecInlineComment keepend skipwhite

syntax region tmspecNonflowStatement start=/\(zone\|component\|type\)/ end=/;/ contained contains=tmspecDeclarationKeyword,tmspecDeclNameType,tmspecDeclBody,tmspecInlineComment skipwhite keepend
syntax region tmspecFlowStatement start=/flow/ end=/;/ contained contains=tmspecDeclarationKeyword,tmspecDeclNameType,tmspecDeclFlowBody,tmspecInlineComment skipwhite keepend

syntax region tmspecDeclNameType start=/[A-Za-z0-9_@]\+/ end=/\(([^)]*)\)\?/ contained contains=tmspecDeclName,tmspecDeclTypes,tmspecInlineComment

syntax region tmspecDeclBody start=/:/ end=/;/ contained contains=tmspecIdentifier,tmspecString,tmspecAssign,tmspecInlineComment keepend skipwhite
syntax region tmspecDeclFlowBody start=/:/ end=/;/ contained contains=tmspecIdentifier,tmspecString,tmspecArrow,tmspecAssign,tmspecInlineComment keepend skipwhite

syntax match tmspecDeclName /[A-Za-z0-9_@]\+/ contained
syntax match tmspecDeclTypes "([^)]*)" contained skipwhite contains=tmspecType,tmspecInlineComment

syntax match tmspecType /[A-Za-z0-9_@]\+/ contained

syntax match tmspecArrow /-->\|<--/ contained skipwhite
syntax match tmspecIdentifier /[A-Za-z0-9_@]\+/ contained 
syntax match tmspecAssign /=/ contained

syntax match tmspecComment /#.*/
syntax region tmspecInlineComment start="/\*" end="\*/"
syntax region tmspecString start=/'/ skip=/\\'/ end=/'/

highlight link tmspecArrow Operator
highlight link tmspecAssign Operator
highlight link tmspecDirectiveKeyword PreProc
highlight link tmspecDeclarationKeyword Statement
highlight link tmspecString String
highlight link tmspecIdentifier Identifier
highlight link tmspecDeclName Function
highlight link tmspecType Type
highlight link tmspecComment Comment
highlight link tmspecInlineComment Comment

