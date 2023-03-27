# Generated from tmspec.g4 by ANTLR 4.9.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .tmspecParser import tmspecParser
else:
    from tmspecParser import tmspecParser

# This class defines a complete listener for a parse tree produced by tmspecParser.
class tmspecListener(ParseTreeListener):

    # Enter a parse tree produced by tmspecParser#start.
    def enterStart(self, ctx:tmspecParser.StartContext):
        pass

    # Exit a parse tree produced by tmspecParser#start.
    def exitStart(self, ctx:tmspecParser.StartContext):
        pass


    # Enter a parse tree produced by tmspecParser#declaration.
    def enterDeclaration(self, ctx:tmspecParser.DeclarationContext):
        pass

    # Exit a parse tree produced by tmspecParser#declaration.
    def exitDeclaration(self, ctx:tmspecParser.DeclarationContext):
        pass


    # Enter a parse tree produced by tmspecParser#component.
    def enterComponent(self, ctx:tmspecParser.ComponentContext):
        pass

    # Exit a parse tree produced by tmspecParser#component.
    def exitComponent(self, ctx:tmspecParser.ComponentContext):
        pass


    # Enter a parse tree produced by tmspecParser#name_and_type.
    def enterName_and_type(self, ctx:tmspecParser.Name_and_typeContext):
        pass

    # Exit a parse tree produced by tmspecParser#name_and_type.
    def exitName_and_type(self, ctx:tmspecParser.Name_and_typeContext):
        pass


    # Enter a parse tree produced by tmspecParser#attributes.
    def enterAttributes(self, ctx:tmspecParser.AttributesContext):
        pass

    # Exit a parse tree produced by tmspecParser#attributes.
    def exitAttributes(self, ctx:tmspecParser.AttributesContext):
        pass


    # Enter a parse tree produced by tmspecParser#attribute.
    def enterAttribute(self, ctx:tmspecParser.AttributeContext):
        pass

    # Exit a parse tree produced by tmspecParser#attribute.
    def exitAttribute(self, ctx:tmspecParser.AttributeContext):
        pass


    # Enter a parse tree produced by tmspecParser#typedef.
    def enterTypedef(self, ctx:tmspecParser.TypedefContext):
        pass

    # Exit a parse tree produced by tmspecParser#typedef.
    def exitTypedef(self, ctx:tmspecParser.TypedefContext):
        pass


    # Enter a parse tree produced by tmspecParser#zone.
    def enterZone(self, ctx:tmspecParser.ZoneContext):
        pass

    # Exit a parse tree produced by tmspecParser#zone.
    def exitZone(self, ctx:tmspecParser.ZoneContext):
        pass


    # Enter a parse tree produced by tmspecParser#versiondef.
    def enterVersiondef(self, ctx:tmspecParser.VersiondefContext):
        pass

    # Exit a parse tree produced by tmspecParser#versiondef.
    def exitVersiondef(self, ctx:tmspecParser.VersiondefContext):
        pass


    # Enter a parse tree produced by tmspecParser#include.
    def enterInclude(self, ctx:tmspecParser.IncludeContext):
        pass

    # Exit a parse tree produced by tmspecParser#include.
    def exitInclude(self, ctx:tmspecParser.IncludeContext):
        pass


    # Enter a parse tree produced by tmspecParser#flow.
    def enterFlow(self, ctx:tmspecParser.FlowContext):
        pass

    # Exit a parse tree produced by tmspecParser#flow.
    def exitFlow(self, ctx:tmspecParser.FlowContext):
        pass


    # Enter a parse tree produced by tmspecParser#arrow.
    def enterArrow(self, ctx:tmspecParser.ArrowContext):
        pass

    # Exit a parse tree produced by tmspecParser#arrow.
    def exitArrow(self, ctx:tmspecParser.ArrowContext):
        pass


    # Enter a parse tree produced by tmspecParser#typing.
    def enterTyping(self, ctx:tmspecParser.TypingContext):
        pass

    # Exit a parse tree produced by tmspecParser#typing.
    def exitTyping(self, ctx:tmspecParser.TypingContext):
        pass


    # Enter a parse tree produced by tmspecParser#value.
    def enterValue(self, ctx:tmspecParser.ValueContext):
        pass

    # Exit a parse tree produced by tmspecParser#value.
    def exitValue(self, ctx:tmspecParser.ValueContext):
        pass


    # Enter a parse tree produced by tmspecParser#boolean.
    def enterBoolean(self, ctx:tmspecParser.BooleanContext):
        pass

    # Exit a parse tree produced by tmspecParser#boolean.
    def exitBoolean(self, ctx:tmspecParser.BooleanContext):
        pass


    # Enter a parse tree produced by tmspecParser#number.
    def enterNumber(self, ctx:tmspecParser.NumberContext):
        pass

    # Exit a parse tree produced by tmspecParser#number.
    def exitNumber(self, ctx:tmspecParser.NumberContext):
        pass


    # Enter a parse tree produced by tmspecParser#identifier.
    def enterIdentifier(self, ctx:tmspecParser.IdentifierContext):
        pass

    # Exit a parse tree produced by tmspecParser#identifier.
    def exitIdentifier(self, ctx:tmspecParser.IdentifierContext):
        pass



del tmspecParser