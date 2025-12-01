from wild.nodes.base import ASTNode
from wild.nodes.expression import *
from wild.nodes.statement import *
from wild.tokens import *
from wild.type.base import RuntimeType
from wild.type.boolean import Boolean
from wild.type.empty import Null
from wild.type.numeric import Float, Integer
from wild.type.strings import String

__all__ = ("Parser",)

class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens: list[Token] = tokens
        self.position: int = 0
    
    def _finish_call(self, callee: ASTNode) -> ASTNode:
        arguments: list[ASTNode] = self._parse_arguments()
        self.consume(TokenType.RPAREN)

        if isinstance(callee, Variable): return FunctionCall(callee.name, arguments)

        error: str = "Invalid function call target"
        raise SyntaxError(error)

    def _parse_arguments(self) -> list[ASTNode]:
        arguments: list[ASTNode] = []

        if self.peek().type != TokenType.RPAREN:
            while True:
                arguments.append(self.parse_expression())
                if not self.match(TokenType.COMMA): break
        
        return arguments

    def consume(self, *types: TokenType) -> Token:
        token: Token = self.peek()
        if token and (not types or token.type in types):
            self.position += 1
            return token
        
        expected: TokenType = types[0].name if types else "any"
        got: TokenType = token.type.name if token else "EOF"

        error: str = f"Expected {expected}, got {got} at line {token.line if token else '?'}"
        raise SyntaxError(error)

    def match(self, *types: TokenType) -> bool:
        token: Token = self.peek()
        if token and token.type in types:
            self.position += 1
            return True
        
        return False

    def parse(self) -> Program:
        statements: list[ASTNode] = []
        while self.peek():
            statements.append(self.parse_statement())
        
        return Program(statements)
    
    def parse_block(self) -> Block:
        self.consume(TokenType.LBRACE)
        statements: list[ASTNode] = []

        while not self.match(TokenType.RBRACE):
            statements.append(self.parse_statement())
        
        return Block(statements)

    def parse_call_and_access(self, expression: ASTNode) -> ASTNode:
        while True:
            if self.match(TokenType.LPAREN):
                expression = self._finish_call(expression)
            elif self.match(TokenType.DOT):
                name_token: TokenType = self.consume(TokenType.IDENTIFIER)
                name: str = name_token.value

                if self.match(TokenType.LPAREN):
                    arguments: list[ASTNode] = self._parse_arguments()
                    self.consume(TokenType.RPAREN)
                    expression: MethodCall = MethodCall(expression, name, arguments)
                else:
                    expression: Get = Get(expression, name)
            else:
                break
        
        return expression

    def parse_comparison(self) -> ASTNode:
        left: ASTNode = self.parse_term()

        while True:
            token: Token = self.peek()
            if token and token.type in (
                TokenType.LESS, TokenType.LESS_EQ,
                TokenType.GREATER, TokenType.GREATER_EQ
            ):
                operator: TokenType = self.consume().type
                right: ASTNode = self.parse_term()
                left: BinaryOperation = BinaryOperation(left, operator, right)
            else:
                break
        
        return left

    def parse_equality(self) -> ASTNode:
        left: ASTNode = self.parse_comparison()

        while True:
            token: Token = self.peek()
            if token and token.type in (TokenType.EQUAL, TokenType.NOT_EQ):
                operator: TokenType = self.consume().type
                right: ASTNode = self.parse_comparison()
                left: BinaryOperation = BinaryOperation(left, operator, right)
            else:
                break
        
        return left

    def parse_expression(self) -> ASTNode | RuntimeType:
        return self.parse_logic_or()

    def parse_factor(self) -> ASTNode:
        left: ASTNode = self.parse_unary()

        while True:
            token: Token = self.peek()
            if token and token.type in (TokenType.MULT, TokenType.DIV, TokenType.MOD):
                operator: TokenType = self.consume().type
                right: ASTNode = self.parse_unary()
                left: BinaryOperation = BinaryOperation(left, operator, right)
            else:
                break
        
        return left

    def parse_for(self) -> For:
        self.consume(TokenType.FOR)
        self.consume(TokenType.LPAREN)

        if self.match(TokenType.SEMICOLON):
            initializer: ASTNode = None
        elif self.peek().type in (TokenType.TYPE_INT, TokenType.TYPE_FLOAT, TokenType.TYPE_STRING):
            initializer: ASTNode = self.parse_variable_declaration()
        else:
            initializer: ASTNode = self.parse_expression()
            self.consume(TokenType.SEMICOLON)
        
        if self.match(TokenType.SEMICOLON):
            condition: ASTNode = Literal(Boolean(True))
        else:
            condition: ASTNode = self.parse_expression()
            self.consume(TokenType.SEMICOLON)
        
        if self.match(TokenType.RPAREN):
            increment: ASTNode = None
        else:
            increment: ASTNode = self.parse_expression()
            self.consume(TokenType.RPAREN)
        
        body: ASTNode = self.parse_statement()
        return For(initializer, condition, increment, body)

    def parse_function_definition(self) -> FunctionDefinition:
        return_type: str = self.consume().value
        name: str = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.LPAREN)
        parameters: list[tuple[str, str]] = []

        if not self.match(TokenType.RPAREN):
            while True:
                parameter_type: str = self.consume().value
                parameter_name: str = self.consume(TokenType.IDENTIFIER).value
                parameters.append((parameter_type, parameter_name))

                if self.match(TokenType.RPAREN): break
                self.consume(TokenType.COMMA)
        
        body: Block = self.parse_block()
        return FunctionDefinition(name, parameters, body, return_type)

    def parse_if(self) -> If:
        self.consume(TokenType.IF)
        
        condition: ASTNode = self.parse_expression()
        branch_true: Block = self.parse_block()
        branch_false: Block | None = None

        if self.match(TokenType.ELSE):
            branch_false = self.parse_block()
        
        return If(condition, branch_true, branch_false)

    def parse_logic_and(self) -> ASTNode:
        left: ASTNode = self.parse_equality()

        while self.match(TokenType.AND):
            right: ASTNode = self.parse_equality()
            left: BinaryOperation = BinaryOperation(left, TokenType.AND, right)
        
        return left

    def parse_logic_or(self) -> ASTNode:
        left: ASTNode = self.parse_logic_and()

        while self.match(TokenType.OR):
            right: ASTNode = self.parse_logic_and()
            left: BinaryOperation = BinaryOperation(left, TokenType.OR, right)
        
        return left

    def parse_postfix(self) -> ASTNode:
        expression: ASTNode = self.parse_primary()

        if self.match(TokenType.PLUS_PLUS):
            if not isinstance(expression, Variable):
                error: str = f"Invalid increment target. Expected variable, got {expression}"
                raise SyntaxError(error)
            
            return Postfix(expression, TokenType.PLUS_PLUS)

        if self.match(TokenType.MINUS_MINUS):
            if not isinstance(expression, Variable):
                error: str = f"Invalid decrement target. Expected variable, got {expression}"
                raise SyntaxError(error)
            
            return Postfix(expression, TokenType.MINUS_MINUS)
        
        return expression

    def parse_primary(self) -> ASTNode:
        if self.match(TokenType.INT_LITERAL): return Literal(Integer(int(self.tokens[self.position - 1].value)))
        if self.match(TokenType.FLOAT_LITERAL): return Literal(Float(float(self.tokens[self.position - 1].value)))
        if self.match(TokenType.STRING_LITERAL): return Literal(String(self.tokens[self.position - 1].value.strip('"').strip('\'')))
        if self.match(TokenType.TRUE): return Literal(Boolean(True))
        if self.match(TokenType.FALSE): return Literal(Boolean(False))
        if self.match(TokenType.NULL): return Literal(Null())
        
        if self.match(TokenType.IDENTIFIER):
            name: str = self.tokens[self.position - 1].value
            expression: Variable = Variable(name)
        elif self.match(TokenType.LPAREN):
            expression: ASTNode = self.parse_expression()
            self.consume(TokenType.RPAREN)
        else:
            error: str = f"Unexpected token {self.peek()}"
            raise SyntaxError(error)
    
        return self.parse_call_and_access(expression)

    def parse_return(self) -> Return:
        self.consume(TokenType.RETURN)
        value: RuntimeType | None = None

        if self.peek().type != TokenType.SEMICOLON:
            value = self.parse_expression()
        
        self.consume(TokenType.SEMICOLON)
        return Return(value)

    def parse_statement(self) -> ASTNode:
        token: Token = self.peek()

        if not token:
            return None

        if token.type in (TokenType.TYPE_INT, TokenType.TYPE_FLOAT, TokenType.TYPE_STRING, TokenType.TYPE_BOOLEAN, TokenType.VOID):
            next: Token = self.peek(1)
            after: Token = self.peek(2)

            if next and next.type == TokenType.IDENTIFIER:
                if after and after.type == TokenType.LPAREN:
                    return self.parse_function_definition()
        
            return self.parse_variable_declaration()
        
        match token.type:
            case TokenType.BREAK:
                self.consume(TokenType.BREAK)
                self.consume(TokenType.SEMICOLON)
                return Break()
            case TokenType.CONTINUE:
                self.consume(TokenType.CONTINUE)
                self.consume(TokenType.SEMICOLON)
                return Continue()
            case TokenType.FOR: return self.parse_for()
            case TokenType.IF: return self.parse_if()
            case TokenType.LBRACE: return self.parse_block()
            case TokenType.RETURN: return self.parse_return()
            case TokenType.WHILE: return self.parse_while()
        
        expression: ASTNode = self.parse_expression()

        if self.match(TokenType.ASSIGN):
            if not isinstance(expression, Variable):
                error: str = "Invalid assignment target"
                raise SyntaxError(error)
            
            value: RuntimeType = self.parse_expression()
            self.consume(TokenType.SEMICOLON)
            return Assignment(expression, value)
        
        if self.match(TokenType.PLUS_EQ):
            value: RuntimeType = self.parse_expression()
            self.consume(TokenType.SEMICOLON)
            return Assignment(expression, BinaryOperation(expression, TokenType.PLUS, value))
        
        if self.match(TokenType.MINUS_EQ):
            value: RuntimeType = self.parse_expression()
            self.consume(TokenType.SEMICOLON)
            return Assignment(expression, BinaryOperation(expression, TokenType.MINUS, value))
        
        if self.match(TokenType.MULT_EQ):
            value: RuntimeType = self.parse_expression()
            self.consume(TokenType.SEMICOLON)
            return Assignment(expression, BinaryOperation(expression, TokenType.MULT, value))
        
        if self.match(TokenType.DIV_EQ):
            value: RuntimeType = self.parse_expression()
            self.consume(TokenType.SEMICOLON)
            return Assignment(expression, BinaryOperation(expression, TokenType.DIV, value))

        if self.match(TokenType.MOD_EQ):
            value: RuntimeType = self.parse_expression()
            self.consume(TokenType.SEMICOLON)
            return Assignment(expression, BinaryOperation(expression, TokenType.MOD, value))
        
        self.consume(TokenType.SEMICOLON)
        return expression

    def parse_term(self) -> ASTNode:
        left: ASTNode = self.parse_factor()

        while True:
            token: Token = self.peek()
            if token and token.type in (TokenType.PLUS, TokenType.MINUS):
                operator: TokenType = self.consume().type
                right: ASTNode = self.parse_term()
                left: BinaryOperation = BinaryOperation(left, operator, right)
            else:
                break
        
        return left

    def parse_unary(self) -> ASTNode:
        if self.match(TokenType.MINUS, TokenType.NOT):
            operator: TokenType = self.tokens[self.position - 1].type
            return UnaryOperation(operator, self.parse_unary())
        
        return self.parse_postfix()

    def parse_variable_declaration(self) -> VariableDeclaration:
        type_name: str = self.consume().value
        name: str = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.ASSIGN)
        value: RuntimeType = self.parse_expression()
        self.consume(TokenType.SEMICOLON)

        return VariableDeclaration(name, type_name, value)
    
    def parse_while(self) -> While:
        self.consume(TokenType.WHILE)

        condition: ASTNode = self.parse_expression()
        body: Block = self.parse_block()

        return While(condition, body)

    def peek(self, offset: int = 0) -> Token | None:
        if self.position + offset >= len(self.tokens): return None
        return self.tokens[self.position + offset]