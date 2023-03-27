# Generated from tmspec.g4 by ANTLR 4.9.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .tmspecParser import tmspecParser
else:
    from tmspecParser import tmspecParser

# This class defines a complete generic visitor for a parse tree produced by tmspecParser.

class tmspecVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by tmspecParser#start.
    def visitStart(self, ctx:tmspecParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#declaration.
    def visitDeclaration(self, ctx:tmspecParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#component.
    def visitComponent(self, ctx:tmspecParser.ComponentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#name_and_type.
    def visitName_and_type(self, ctx:tmspecParser.Name_and_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#attributes.
    def visitAttributes(self, ctx:tmspecParser.AttributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#attribute.
    def visitAttribute(self, ctx:tmspecParser.AttributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#typedef.
    def visitTypedef(self, ctx:tmspecParser.TypedefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#zone.
    def visitZone(self, ctx:tmspecParser.ZoneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#versiondef.
    def visitVersiondef(self, ctx:tmspecParser.VersiondefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#include.
    def visitInclude(self, ctx:tmspecParser.IncludeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#flow.
    def visitFlow(self, ctx:tmspecParser.FlowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#arrow.
    def visitArrow(self, ctx:tmspecParser.ArrowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#typing.
    def visitTyping(self, ctx:tmspecParser.TypingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#value.
    def visitValue(self, ctx:tmspecParser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#boolean.
    def visitBoolean(self, ctx:tmspecParser.BooleanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#number.
    def visitNumber(self, ctx:tmspecParser.NumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tmspecParser#identifier.
    def visitIdentifier(self, ctx:tmspecParser.IdentifierContext):
        return self.visitChildren(ctx)



del tmspecParser