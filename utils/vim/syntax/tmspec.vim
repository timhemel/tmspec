syntax clear
syntax case match

syntax keyword tmspecDirectiveKeyword version include contained skipwhite
syntax region tmspecDirective start=/version\|include/ end=/;/ contains=tmspecDirectiveKeyword,tmspecInlineComment

syntax region tmspecDeclaration start=/\(zone\|component\|type\|flow\)\s*/ end=/;/ contains=tmspecDeclStatement,tmspecDeclStatementFlow,tmspecInlineComment keepend skip=tmspecInlineComment

syntax match tmspecDeclStatement /\(zone\|component\|type\)/ contained nextgroup=tmspecDeclNameType skipwhite
syntax match tmspecDeclNameType /[A-Za-z0-9_@]\+\(([^)]*)\)\?/ contained contains=tmspecDeclName,tmspecInlineComment nextgroup=tmspecDeclBody
syntax region tmspecDeclBody start=/:/ end=/;/ contained contains=tmspecProperty,tmspecInlineComment keepend skipwhite

syntax match tmspecDeclStatementFlow /flow/ contained nextgroup=tmspecDeclNameTypeFlow skipwhite
syntax match tmspecDeclNameTypeFlow /[A-Za-z0-9_@]\+\(([^)]*)\)\?/ contained contains=tmspecDeclName nextgroup=tmspecDeclBodyFlow
syntax region tmspecDeclBodyFlow start=/:/ end=/;/ contained contains=tmspecFlow,tmspecInlineComment keepend skipwhite

syntax match tmspecDeclName /[A-Za-z0-9_@]\+/ contained nextgroup=tmspecInherit skipwhite
syntax match tmspecInherit /([^)]*)\|/ contained skipwhite contains=tmspecType,tmspecInlineComment
syntax match tmspecType /[A-Za-z0-9_@]\+/ contained

" syntax match tmspecFlow /\([A-Za-z0-9_@]\+\s*\(-->\|<--\)\s*[A-Za-z0-9_@]\+\s*[,;]\)/ contained nextgroup=tmspecProperty skipwhite contains=tmspecArrow,tmspecIdentifier,tmspecInlineComment
syntax match tmspecFlow /.*\(-->\|<--\).*[,;]/ contained nextgroup=tmspecProperty skipwhite contains=tmspecArrow,tmspecIdentifier,tmspecInlineComment
syntax region tmspecProperty start=/[A-Za-z0-9_@]\|'/ end=/[,;]/ contained contains=tmspecIdentifier,tmspecString,tmspecAssign,tmspecInlineComment nextgroup=tmspecProperty skipwhite

syntax match tmspecArrow /-->\|<--/ contained skipwhite
syntax match tmspecIdentifier /[A-Za-z0-9_@]\+/ contained 
syntax match tmspecAssign /=/ contained

syntax match tmspecComment /#.*/
" TODO: /* comment */
syntax region tmspecInlineComment start="/\*" end="\*/"
syntax region tmspecString start=/'/ skip=/\\'/ end=/'/

highlight link tmspecArrow Operator
highlight link tmspecAssign Operator
highlight link tmspecOperator Operator
highlight link tmspecDeclStatement Statement
highlight link tmspecDeclStatementFlow Statement
highlight link tmspecDirectiveKeyword PreProc
highlight link tmspecString String
highlight link tmspecIdentifier Identifier
highlight link tmspecDeclName Function
highlight link tmspecType Type
highlight link tmspecComment Comment
highlight link tmspecInlineComment Comment

