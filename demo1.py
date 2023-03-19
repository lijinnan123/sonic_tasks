from enum import IntEnum
from typing import NamedTuple
import string

TEST_PROGRAM = """
var i, s;
begin
    i := 0; s := 0;
    while i < 5 do
    begin
        i := i + 1;
        s := s + i * i
    end
end.
"""

IDENT_FIRST = string.ascii_letters + '_'
IDENT_REMAIN = string.ascii_letters + string.digits + '_'

KEYWORD_SET = {
    'const',
    'var',
    'procedure',
    'call',
    'begin',
    'end',
    'if',
    'then',
    'while',
    'do',
    'odd',
}

class TokenKind(IntEnum):
    Op      = 0
    Num     = 1
    Name    = 2
    Keyword = 3
    Eof     = 4

class Token(NamedTuple):
    ty      : TokenKind
    val     : int | str

    @classmethod
    def op(cls, op: str) -> 'Token':
        return cls(ty = TokenKind.Op, val = op)

    @classmethod
    def num(cls, num: int) -> 'Token':
        return cls(ty = TokenKind.Num, val = num)
    
    @classmethod
    def name(cls, name: str) -> 'Token':
        return cls(ty = TokenKind.Name, val = name)

    @classmethod
    def keyword(cls, keyword: str) -> 'Token':
        return cls(ty = TokenKind.Keyword, val = keyword)
    
    @classmethod
    def eof(cls) -> 'Token':
        return cls(ty = TokenKind.Eof, val = 0)

class Lexer:
    i: int
    s: str

    def __init__(self, src: str):
        self.i = 0
        self.s = src

    @property
    def eof(self) -> bool:
        return self.i >= len(self.s)

    def _skip_blank(self):
        while not self.eof and self.s[self.i].isspace():
            self.i += 1

    def next(self) -> Token:
        val = ''
        self._skip_blank()
        if self.eof:
            return Token.eof()

        elif self.s[self.i].isdigit():
            while self.s[self.i].isdigit():
                val += self.s[self.i]
                self.i += 1
            return Token.num(int(val))

        elif self.s[self.i] in IDENT_FIRST:
            while self.s[self.i] in IDENT_REMAIN:
                val += self.s[self.i]
                self.i += 1
        
            if val in KEYWORD_SET:
                return Token.keyword(val)
            else:
                return Token.name(val)

        elif self.s[self.i] in '=#+-*/,.;()':
            ch = self.s[self.i]
            self.i += 1
            return Token.op(ch)

        elif self.s[self.i] == ':':
            self.i += 1

            if self.eof or self.s[self.i] != '=':
                raise SyntaxError('"=" expected' ) # 这里报错，其他的地方为啥不报错
            
            self.i += 1
            return Token.op(':=')
        
        elif self.s[self.i] in '><':
            ch = self.s[self.i]
            self.i += 1
            if not self.eof and self.s[self.i] == '=':
                self.i += 1
                return Token.op(ch + '=')

            else:
                return Token.op(ch)
        
        else:
            raise SyntaxError('invalid character' + repr(self.s[self.i]))

# lx = Lexer(TEST_PROGRAM)
# tk = lx.next()
# while tk.ty != TokenKind.Eof:
#     print(tk)
#     tk = lx.next()

class Const(NamedTuple):
    name    : str
    value   : int

class Factor(NamedTuple):
    value   : 'str | int | Expression'

class Term(NamedTuple):
    lhs     : Factor
    rhs     : list[tuple[str, Factor]]

class Expression(NamedTuple):
    mod     : str
    term    : 'Term'
    rhs     : list[tuple[str, Term]]

class Assign(NamedTuple):
    name    : str
    expr    : Expression

class Procedure(NamedTuple):
    name    : str
    body    : 'Block'

class Call(NamedTuple):
    name    : str

class Begin(NamedTuple):
    body    : list['Statement']

class OddCondition(NamedTuple):
    expr    : Expression

class StdCondition(NamedTuple):
    op      : str
    lhs     : Expression
    rhs     : Expression

class Condition(NamedTuple):
    cond    : OddCondition | StdCondition

class If(NamedTuple):
    cond    : Condition
    then    : 'Statement'

class While(NamedTuple):
    cond    : Condition
    do      : 'Statement'

class Statement(NamedTuple):
    stmt: Assign | Call | Begin | If | While

class Var(NamedTuple):
    name    : str

class Block(NamedTuple):
    const   : list[Const]
    vars    : list[Var]
    procs   : list[Procedure]
    stmt    : Statement

class Program(NamedTuple):
    block   : 'Block'

# []:0-1
# {}:0-*

class Parser:
    lx : Lexer
    
    def __init__(self, lx : Lexer):
        self.lx = lx

    # 看下一个token是不是这个，是的话就吃掉，不是的话就返回false，算是支持反复检查的回滚操作
    def check(self, ty : TokenKind, val : str | int) -> bool:
        p = self.lx.i
        tk = self.lx.next()
        
        if tk.ty == ty and tk.val == val:
            return True
        
        self.lx.i = p
        return False

    # 下一个token必须是啥
    def expect(self, ty : TokenKind, val: str | int | None = None):
        tk = self.lx.next()
        tty, tval = tk.ty, tk.val
        
        if tty != ty:
            raise SyntaxError('%s expected, got %s' % (ty, tty))
        
        if val is not None:
            if tval != val:
                raise SyntaxError('"%s" expected, got "%s"' % (val, tval))
    
    def factor(self) -> Factor:
        ident = self.lx.next()
        if ident.ty == TokenKind.Name:
            return Factor(ident.val)
        elif ident.ty == TokenKind.Num:
            return Factor(ident.val)
        elif ident.ty == TokenKind.Op and ident.val == '(':
            expr = self.expression()
            self.expect(TokenKind.Op, ')')
            return Factor(expr)

    def term(self) -> Term:
        fac1 = self.factor()
        if self.check(TokenKind.Op, '.'):
            return Factor(fac1)
        fac_list = []
        p = self.lx.i
        token = self.lx.next()
        while(token.val == '*' or token.val == '/'):
            fac_list.append((token.val, self.factor()))
            p = self.lx.i
            token = self.lx.next()
        
        self.lx.i = p
        return Term(fac1, fac_list)

    def expression(self) -> Expression:
        p = self.lx.i
        token = self.lx.next()
        if token.val == '+' or token.val == '-':
            te = self.term()
        else:
            self.lx.i = p
            token = ''
            te = self.term()
        term_list = []
        p = self.lx.i
        ttoken = self.lx.next()
        while(ttoken.val == '+' or ttoken.val == '-'):
            term_list.append((ttoken.val, self.term()))
            p = self.lx.i
            ttoken = self.lx.next()
        self.lx.i = p
        return Expression(token, te, term_list)

    def condition(self) -> Condition:
        if self.check(TokenKind.Keyword, 'odd'):
            expr = self.expression()
            return Condition(OddCondition(expr))
        else:
            expr1 = self.expression()
            token = self.lx.next()
            if token.val not in ['=', '#', '<', '>', '<=', '>=']:
                raise SyntaxError('condition syntax error')
            expr2 = self.expression()
            return Condition(StdCondition(token.val, expr1, expr2))

    def begin(self) -> Begin:
        stat_list = []
        stat_list.append(self.statement())
        token = self.lx.next()
        while(token.val == ';'):
            stat_list.append(self.statement())
            token = self.lx.next()
        if token.val == 'end':
            return Begin(stat_list)
        else:
            raise SyntaxError('end is expected')

    def call(self) -> Call:
        ident = self.lx.next()
        if ident.ty != TokenKind.Name:
            raise SyntaxError('name expected')
        else:
            return Call(ident.val)

    def if_(self) -> If:
        cond = self.condition()
        if self.check(TokenKind.Keyword, 'then'):
            stat = self.statement()
            return If(cond, stat)
        else:
            raise SyntaxError("then is expected")
    
    def while_(self) -> While:
        cond = self.condition()
        if self.check(TokenKind.Keyword, 'do'):
            stat = self.statement()
            return While(cond, stat)
        else:
            raise SyntaxError("do is expected")

    def assign(self) -> Assign:
        ident = self.lx.next()
        if ident.ty != TokenKind.Name:
            raise SyntaxError('assign ident name error')
        self.expect(TokenKind.Op, ':=')
        expr = self.expression()
        return Assign(ident.val, expr)

    def statement(self) -> Statement:
        if self.check(TokenKind.Keyword, 'call'):
            return Statement(self.call())
        elif self.check(TokenKind.Keyword, 'begin'):
            return Statement(self.begin())
        elif self.check(TokenKind.Keyword, 'if'):
            return Statement(self.if_())
        elif self.check(TokenKind.Keyword, 'while'):
            return Statement(self.while_())
        else:
            return Statement(self.assign())

    def const(self) -> Const:
        ident = self.lx.next()
        if ident.ty != TokenKind.Name:
            raise SyntaxError('const ident name error')
        if self.check(TokenKind.Op, '='):
            num = self.lx.next()
            if num.ty != TokenKind.Num:
                raise SyntaxError('const num error')
            return Const(ident.val, num.val)
        else:
            raise SyntaxError('const = is expected')

    def var(self) -> Var:
        ident = self.lx.next()
        if ident.ty != TokenKind.Name:
            raise SyntaxError('var ident type error')
        else:
            return Var(ident.val)

    def procedure(self) -> Procedure:
        ident = self.lx.next()
        if ident.ty != TokenKind.Name:
            raise SyntaxError('pro ident type error')
        self.expect(TokenKind.Op, ';')
        bk = self.block()
        self.expect(TokenKind.Op, ';')
        return Procedure(ident.val, bk)

    def block(self) -> Block:
        const_list = []
        var_list = []
        pro_list = []

        if self.check(TokenKind.Keyword, 'const'):
            const_list.append(self.const())
            token = self.lx.next()
            while(token.val != ';' and token.val == ','):
                const_list.append(self.const())
                token = self.lx.next()
        if self.check(TokenKind.Keyword, 'var'):
            var_list.append(self.var())
            token = self.lx.next()
            while(token.val != ';' and token.val == ','):
                var_list.append(self.var())
                token = self.lx.next()
        while(self.check(TokenKind.Keyword, 'procedure')):
            pro_list.append(self.procedure())

        stat = self.statement()
        return Block(const_list, var_list, pro_list, stat)

    def program(self) -> 'Program':
        block = self.block()
        self.expect(TokenKind.Op, '.')
        return Program(block)
        
parser = Parser(Lexer(TEST_PROGRAM))
prog = parser.program()
print(prog)
