from enum import IntEnum
from typing import NamedTuple
import string
import copy

TEST_PROGRAM ="""
var i, s;
procedure nnd;
    var t;
    begin
        i := 7
    end
;
begin
    i := 0; s := 0;
    while i < 5 do
    begin
        i := i + 1;
        s := s + i * i
    end;
    call nnd
end.
"""


"""
var x, squ;

procedure square;
begin
   squ:= x * x
end;

begin
   x := 1;
   while x <= 10 do
   begin
      call square;
      x := x + 1
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

class IrOpCode(IntEnum):
    # 从算术的角度出发
    Add     = 0
    Sub     = 1
    Mul     = 2
    Div     = 3
    # 比较运算符
    Neg     = 4
    Eq      = 5
    Ne      = 6
    Lt      = 7
    Lte     = 8
    Gt      = 9
    Gte     = 10
    Odd     = 11
    LoadVar = 12
    LoadLit = 13
    Store   = 14
    Jump    = 15
    BrFalse = 16
    DefVar  = 17
    DefLit  = 18
    DefProc = 19
    Call    = 20
    Halt    = 255

# N元操作符
class Ir(NamedTuple):
    op    : IrOpCode
    args  : str | int | None        = None
    value : int | list['Ir'] | None = None

# 怎么想到这些数据结构的？
class EvalContext(NamedTuple):
    vars   : dict[str, list[int | None, int, bool]]
    procs  : dict[str, 'Block | list[Ir]']
    consts : dict[str, list[int, int, bool]]

class Const(NamedTuple):
    name    : str
    value   : int

    def gen(self, buf: list[Ir]):
        buf.append(Ir(IrOpCode.DefLit, self.name, self.value))
        # 这里怎么和eval对应？

    def eval(self, ctx: EvalContext) -> int | None :
        key = self.name
        value = self.value
        
        if key not in ctx.consts and key not in ctx.vars:
            ctx.consts[key] = [value, 0, False]
        elif key in ctx.vars and ctx.vars[key][1] != 0:
            ctx.consts[key] = [value, 0, False]
            del ctx.vars[key]
        elif key in ctx.consts and ctx.consts[key][1] != 0:
            ctx.consts[key] = [value, 0, False]
        else:
            raise RuntimeError('multiple definition const')

class Factor(NamedTuple):
    value   : 'str | int | Expression'

    def gen(self, buf: list[Ir]):
        if isinstance(self.value, int):
            buf.append(Ir(IrOpCode.LoadLit, self.value))
        elif isinstance(self.value, str): # 不管是const定义的还是var定义的
            buf.append(Ir(IrOpCode.LoadVar, self.value))
        elif isinstance(self.value, Expression):
            self.value.gen(buf)
        else:
            raise RuntimeError('invalid factor value')

    def eval(self, ctx: EvalContext) -> int | None :
        if isinstance(self.value, int):
            return self.value

        elif isinstance(self.value, str):
            if self.value in ctx.vars:
                key = self.value
                ret = ctx.vars[key][0]

                if ret is None:
                    raise RuntimeError('variable %s referenced before initialize' % key)
                else:
                    return ret
            
            elif self.value in ctx.consts:
                return ctx.consts[self.value][0]
                
            else:
                raise RuntimeError('undefined symbol: ' + self.value)

        elif isinstance(self.value, Expression):
            val = self.value.eval(ctx)
            assert val is not None, 'invalid nested expression' # 这里为什么用assert而不用raise error，要是这里能用，那全文都用assert不行吗
            return val
        
        else:
            raise RuntimeError('invalid factor value')

class Term(NamedTuple):
    lhs     : Factor
    rhs     : list[tuple[str, Factor]]

    def gen(self, buf: list[Ir]):
        self.lhs.gen(buf)
        
        for op, rhs in self.rhs:
            rhs.gen(buf)

            if op == '*':
                buf.append(Ir(IrOpCode.Mul))
            elif op == '/':
                buf.append(Ir(IrOpCode.Div))
            else:
                raise RuntimeError('invalid expression operator')
    
    def eval(self, ctx: EvalContext) -> int | None:
        lhs = self.lhs.eval(ctx)
        assert lhs is not None, 'invalid term lhs'
        ret = lhs
        for op, rhs in self.rhs:
            val = rhs.eval(ctx)
            assert val is not None, 'invalid term rhs'
            
            if op == '*':
                ret *= val
            elif op == '/' and val != 0:
                ret /= val
            elif op == '/' and val == 0:
                raise RuntimeError('div 0 error')
            else:
                raise RuntimeError('invalid expression operator')

        return ret

class Expression(NamedTuple):
    mod     : str
    term    : 'Term'
    rhs     : list[tuple[str, Term]]

    def gen(self, buf: list[Ir]):
        self.term.gen(buf)

        if self.mod == '-':
            buf.append(Ir(IrOpCode.Neg))
        elif self.mod not in {'', '+'}:
            raise RuntimeError('invalid expression sign')

        for op, rhs in self.rhs:
            rhs.gen(buf)

            if op == '+':
                buf.append(Ir(IrOpCode.Add))
            elif op == '-':
                buf.append(Ir(IrOpCode.Sub))
            else:
                raise RuntimeError('invalid expression operator')

    def eval(self, ctx: EvalContext) -> int | None:
        if self.mod == '-':
            sign = -1
        elif self.mod in {'', '+'}:
            sign = 1
        else:
            raise RuntimeError('invalid expression sign')

        ret = self.term.eval(ctx) * sign
        assert ret is not None, 'invalid expression term'
        
        for op, rhs in self.rhs:
            val = rhs.eval(ctx)
            assert val is not None, 'invalid expression rhs'
            
            if op == '+':
                ret += val
            elif op == '-':
                ret -= val
            else:
                raise RuntimeError('invalid expression operator')

        return ret

class Assign(NamedTuple):
    name    : str
    expr    : Expression

    def gen(self, buf: list[Ir]):
        self.expr.gen(buf)
        buf.append(Ir(IrOpCode.Store, self.name))
        # 不晓得这里面的报错是咋样的

    # 不返回值就是返回了None值
    def eval(self, ctx: EvalContext) -> int | None:
        expr = self.expr.eval(ctx)
        assert expr is not None, 'invalid assignment'
        if self.name in ctx.consts:
            raise RuntimeError('assign a const is not permitted')
        elif self.name in ctx.vars:
            ctx.vars[self.name][0] = expr
        else:
            raise RuntimeError('assign before definite')
        
        print(expr)

class Procedure(NamedTuple):
    name    : str
    body    : 'Block'

    def gen(self, buf: list[Ir]):
        pir = []
        if isinstance(self.name, str):
            self.body.gen(pir)
            buf.append(Ir(IrOpCode.DefProc, self.name, pir))
        else:
            raise RuntimeError('invalid definition of procedure name')

    def eval(self, ctx: EvalContext) -> int | None:
        if not isinstance(self.body, Block):
            raise RuntimeError('invalid defpro type')
        else:
            ctx.procs[self.name] = self.body

class Call(NamedTuple):
    name    : str

    def gen(self, buf: list[Ir]):
        buf.append(Ir(IrOpCode.Call, self.name))

    # 问题是全局变量和局部变量重名咋办？
    def eval(self, ctx: EvalContext) -> int | None:
        # local_ctx = EvalContext({}, {}, {})
        # if self.name not in ctx.procs:
        #     raise RuntimeError('call before procedure is defined')
        # else:
        #     ctx.procs[self.name].eval(local_ctx)
        
        key = self.name

        if key not in ctx.procs:
            raise RuntimeError('call procedure before definition')
        tctx = copy.deepcopy(ctx)
        ctx = EvalContext({}, {}, {})
        for each in tctx.vars:
            ctx.vars[each] = [tctx.vars[each][0], tctx.vars[each][1]+1, False]
        for each in tctx.consts:
            ctx.consts[each] = [tctx.consts[each][0], tctx.consts[each][1]+1, False]
        for each in tctx.procs:
            ctx.procs[each] = tctx.procs[each]
        # 此处我的理解是sp不用变换
        ctx.procs[key].eval(ctx)
        for each in tctx.vars:
            # 在下一层修改了一个全局变量
            if each in ctx.vars and ctx.vars[each][1] == tctx.vars[each][1]+1 and ctx.vars[each][2] == True:
                tctx.vars[each] = [tctx.vars[each][0], tctx.vars[each][1], True]
            # 在下一层定义了与全局变量同名的局部变量，在下一层没有修改全局变量，在下一层去掉了这个变量
            else:
                continue
        ctx = copy.deepcopy(tctx)

class Begin(NamedTuple):
    body    : list['Statement']

    def gen(self, buf: list[Ir]):
        for body in self.body:
            body.gen(buf)

    def eval(self, ctx: EvalContext) -> int | None:
        for body in self.body:
            body.eval(ctx)

class OddCondition(NamedTuple):
    expr    : Expression

    def gen(self, buf: list[Ir]):
        self.expr.gen(buf)
        buf.append(Ir(IrOpCode.Odd))
    
    def eval(self, ctx: EvalContext) -> int | None:
        expr = self.expr.eval(ctx)
        assert expr is not None, 'invalid odd expression'

        return expr & 1

class StdCondition(NamedTuple):
    op      : str
    lhs     : Expression
    rhs     : Expression

    def gen(self, buf: list[Ir]):
        self.lhs.gen(buf)
        self.rhs.gen(buf)
        
        if self.op == '=':
            buf.append(Ir(IrOpCode.Eq))
        elif self.op == '#':
            buf.append(Ir(IrOpCode.Ne))
        elif self.op == '<':
            buf.append(Ir(IrOpCode.Lt))
        elif self.op == '<=':
            buf.append(Ir(IrOpCode.Lte))
        elif self.op == '>':
            buf.append(Ir(IrOpCode.Gt))
        elif self.op == '>=':
            buf.append(Ir(IrOpCode.Gte))
        else:
            raise RuntimeError('invalid op type (%s)' % self.op)

    def eval(self, ctx: EvalContext) -> int | None:
        lhs = self.lhs.eval(ctx)
        assert lhs is not None, 'invalid condition lhs'
        rhs = self.rhs.eval(ctx)
        assert rhs is not None, 'invalid condition rhs'

        if self.op == '=':
            return 1 if lhs == rhs else 0
        elif self.op == '#':
            return 1 if lhs != rhs else 0
        elif self.op == '<':
            return 1 if lhs < rhs else 0
        elif self.op == '<=':
            return 1 if lhs <= rhs else 0
        elif self.op == '>':
            return 1 if lhs > rhs else 0
        elif self.op == '>=':
            return 1 if lhs >= rhs else 0
        else:
            raise RuntimeError('invalid op type (%s)' % self.op)

class Condition(NamedTuple):
    cond    : OddCondition | StdCondition

    def gen(self, buf: list[Ir]):
        self.cond.gen(buf)
    
    def eval(self, ctx: EvalContext) -> int | None:
        return self.cond.eval(ctx)        

class If(NamedTuple):
    cond    : Condition
    then    : 'Statement'

    def gen(self, buf: list[Ir]):
        self.cond.gen(buf)
        i = len(buf)
        buf.append(Ir(IrOpCode.BrFalse))
        self.then.gen(buf)
        buf[i] = Ir(IrOpCode.BrFalse, len(buf)) # 太妙了，就是跳到的位置是最后的位置

    def eval(self, ctx: EvalContext) -> int | None:
        cond = self.cond.eval(ctx)
        assert cond is not None, 'invalid if condition expression' # 很多地方都不能为空，都得检查下

        if cond != 0:
            self.then.eval(ctx)            

class While(NamedTuple):
    cond    : Condition
    do      : 'Statement'

    def gen(self, buf: list[Ir]):
        i = len(buf)
        self.cond.gen(buf)
        j = len(buf)
        buf.append(Ir(IrOpCode.BrFalse))
        self.do.gen(buf)
        buf[j] = Ir(IrOpCode.BrFalse, len(buf)+1)
        buf.append(Ir(IrOpCode.Jump, i))

    def eval(self, ctx: EvalContext) -> int | None:
        cond = self.cond.eval(ctx)
        assert cond is not None, 'invalid while condition expression'

        while cond != 0:
            self.do.eval(ctx)
            cond = self.cond.eval(ctx)
            assert cond is not None, 'invalid while condition expression'

class Statement(NamedTuple):
    stmt: Assign | Call | Begin | If | While

    def gen(self, buf: list[Ir]):
        self.stmt.gen(buf)

    def eval(self, ctx: EvalContext) -> int | None:
        self.stmt.eval(ctx)

class Var(NamedTuple):
    name    : str

    def gen(self, buf: list[Ir]):
        buf.append(Ir(IrOpCode.DefVar, self.name))

    def eval(self, ctx: EvalContext) -> int | None:
        key = self.name
        # 在上一层以及之前都没定义过
        if key not in ctx.vars and key not in ctx.consts:
            ctx.vars[key] = [None, 0, False]
        # 在上一层的变量里定义过
        elif key in ctx.vars and ctx.vars[key][1] != 0:
            ctx.vars[key] = [None, 0, False]
        # 在上一层的常量里定义过
        elif key in ctx.consts and ctx.consts[key][1] != 0:
            ctx.vars[key] = [None, 0, False]
            del ctx.consts[key]
        else:
            raise RuntimeError('multiple definition var')

class Block(NamedTuple):
    const   : list[Const]
    vars    : list[Var]
    procs   : list[Procedure]
    stmt    : Statement

    def gen(self, buf: list[Ir]):
        for const in self.const:
            const.gen(buf)
        for var in self.vars:
            var.gen(buf)
        for proc in self.procs:
            proc.gen(buf)
        self.stmt.gen(buf)

    def eval(self, ctx: EvalContext) -> int | None:
        for const in self.const:
            const.eval(ctx)
        for var in self.vars:
            var.eval(ctx)
        for proc in self.procs:
            proc.eval(ctx)
        self.stmt.eval(ctx)

class Program(NamedTuple):
    block   : 'Block'

    def gen(self, buf: list[Ir]):
        self.block.gen(buf)
        buf.append(Ir(IrOpCode.Halt))

    def eval(self, ctx: EvalContext) -> int | None:
        return self.block.eval(ctx)

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
        else:
            raise SyntaxError('factor type error')

    def term(self) -> Term:
        fac1 = self.factor()
        if self.check(TokenKind.Op, '.'):
            return Factor(fac1)
        fac_list = []
        p = self.lx.i
        token = self.lx.next()
        while token.val == '*' or token.val == '/':
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
            mod = token.val
        else:
            self.lx.i = p
            mod = ''
            te = self.term()
        term_list = []
        p = self.lx.i
        ttoken = self.lx.next()
        while ttoken.val == '+' or ttoken.val == '-':
            term_list.append((ttoken.val, self.term()))
            p = self.lx.i
            ttoken = self.lx.next()
        self.lx.i = p
        return Expression(mod, te, term_list)

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
        while token.val == ';':
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
            while token.val != ';' and token.val == ',':
                const_list.append(self.const())
                token = self.lx.next()
            if token.val != ';':
                raise SyntaxError('invalid line end syntax')
        if self.check(TokenKind.Keyword, 'var'):
            var_list.append(self.var())
            token = self.lx.next()
            while token.val != ';' and token.val == ',':
                var_list.append(self.var())
                token = self.lx.next()
            if token.val != ';':
                raise SyntaxError('invalid line end syntax')
        while self.check(TokenKind.Keyword, 'procedure'):
            pro_list.append(self.procedure())

        stat = self.statement()
        return Block(const_list, var_list, pro_list, stat)

    def program(self) -> 'Program':
        block = self.block()
        self.expect(TokenKind.Op, '.')
        return Program(block)


def ir_eval(buf: list[Ir], ctx: EvalContext):
    pc = 0 # 因为是模拟cpu，所以是pc，模拟的指令计数器，运算符从调用栈里搞，操作数暂存到sp里
    sp = [] # 模拟的调用栈
    while pc < len(buf):
        ir = buf[pc]
        pc += 1

        # 就是从末尾pop的
        if ir.op == IrOpCode.Add:
            v2 = sp.pop()
            v1 = sp.pop()
            sp.append(v1 + v2)

        elif ir.op == IrOpCode.Sub:
            v2 = sp.pop()
            v1 = sp.pop()
            sp.append(v1 - v2)

        elif ir.op == IrOpCode.Mul:
            v2 = sp.pop()
            v1 = sp.pop()
            sp.append(v1 * v2)

        # 状态机的感觉，报错在状态机里报错
        elif ir.op == IrOpCode.Div:
            v2 = sp.pop()
            v1 = sp.pop()
            if v2 == 0:
                raise RuntimeError('divided by zero')
            else:
                sp.append(v1 / v2)

        elif ir.op == IrOpCode.Neg:
            v = sp.pop()
            sp.append(-v)

        elif ir.op == IrOpCode.Eq:
            v2 = sp.pop()
            v1 = sp.pop()
            if v1 == v2:
                sp.append(1)
            else:
                sp.append(0)
        
        elif ir.op == IrOpCode.Ne:
            v2 = sp.pop()
            v1 = sp.pop()
            if v1 != v2:
                sp.append(1)
            else:
                sp.append(0)

        elif ir.op == IrOpCode.Gt:
            v2 = sp.pop()
            v1 = sp.pop()
            if v1 > v2:
                sp.append(1)
            else:
                sp.append(0)
        
        elif ir.op == IrOpCode.Lt:
            v2 = sp.pop()
            v1 = sp.pop()
            if v1 < v2:
                sp.append(1)
            else:
                sp.append(0)
            
        elif ir.op == IrOpCode.Gte:
            v2 = sp.pop()
            v1 = sp.pop()
            if v1 >= v2:
                sp.append(1)
            else:
                sp.append(0)

        elif ir.op == IrOpCode.Lte:
            v2 = sp.pop()
            v1 = sp.pop()
            if v1 <= v2:
                sp.append(1)
            else:
                sp.append(0)
        
        elif ir.op == IrOpCode.Odd:
            v = sp.pop()
            sp.append(v & 1)
            
        # 这是数据结构重复利用了下！为什么还要重复利用呢？
        # 对这个数据结构的利用是相当于CPU里的堆吗
        # 这里的load是从数据结构里load，store也是存到数据结构里
        elif ir.op == IrOpCode.LoadVar:
            if not isinstance(ir.args, str):
                raise RuntimeError('invalid loadvar args')
            
            elif ir.args in ctx.vars:
                key = ir.args
                val = ctx.vars[key][0]

                if val is None:
                    raise RuntimeError('variable %s referenced before initialization' % key)
                else:
                    sp.append(val)

            elif ir.args in ctx.consts:
                sp.append(ctx.consts[ir.args][0])
            
            else:
                raise RuntimeError('undefined variable: ' + ir.args)
            
        elif ir.op == IrOpCode.LoadLit:
            if not isinstance(ir.args, int):
                raise RuntimeError('invalid loadlit args')
            else:
                sp.append(ir.args)
                
        elif ir.op == IrOpCode.Store:
            v = sp.pop()
            if not isinstance(ir.args, str):
                raise RuntimeError('invalid store args')
            elif ir.args not in ctx.vars: # 这里默认常量不可修改
                raise RuntimeError('change before define vars')
            else:
                ctx.vars[ir.args][0] = v
                ctx.vars[ir.args][2] = True

        elif ir.op == IrOpCode.Jump:
            if not isinstance(ir.args, int):
                raise RuntimeError('invalid jump args')
            else:
                pc = ir.args

        elif ir.op == IrOpCode.BrFalse:
            if not isinstance(ir.args, int):
                raise RuntimeError('invalid brfalse args')
            else:
                pc = ir.args

        elif ir.op == IrOpCode.DefVar:
            if not isinstance(ir.args, str):
                raise RuntimeError('invalid defvar args')

            key = ir.args
            # 在上一层以及之前都没定义过
            if key not in ctx.vars and key not in ctx.consts:
                ctx.vars[key] = [None, 0, False]
            # 在上一层的变量里定义过
            elif key in ctx.vars and ctx.vars[key][1] != 0:
                ctx.vars[key] = [None, 0, False]
            # 在上一层的常量里定义过
            elif key in ctx.consts and ctx.consts[key][1] != 0:
                ctx.vars[key] = [None, 0, False]
                del ctx.consts[key]
            else:
                raise RuntimeError('multiply definition :' + ir.args)

        elif ir.op == IrOpCode.DefLit:
            # 定义即覆盖
            if not isinstance(ir.args, str):
                raise RuntimeError('invalid deflit args')

            if not isinstance(ir.value, int):
                raise RuntimeError('invalid deflit value')

            key = ir.args
            if key not in ctx.vars and key not in ctx.consts:
                ctx.consts[key] = [ir.value, 0, False]
            elif key in ctx.vars and ctx.vars[key][1] != 0:
                ctx.consts[key] = [ir.value, 0, False]
                del ctx.vars[key]
            elif key in ctx.consts and ctx.consts[key][1] != 0:
                ctx.consts[key] = [ir.value, 0, False]
            else:
                raise RuntimeError('multiply definition :' + ir.args)

        elif ir.op == IrOpCode.DefProc:
            if not isinstance(ir.args, str):
                raise RuntimeError('invalid defproc args')
            elif not isinstance(ir.value, list):
                raise RuntimeError('invalid defproc value')
            else:
                ctx.procs[ir.args] = ir.value

        elif ir.op == IrOpCode.Call:
            if ir.args not in ctx.procs:
                raise RuntimeError('call procedure before definition')
            tctx = copy.deepcopy(ctx)
            ctx = EvalContext({}, {}, {})
            for each in tctx.vars:
                ctx.vars[each] = [tctx.vars[each][0], tctx.vars[each][1]+1, False]
            for each in tctx.consts:
                ctx.consts[each] = [tctx.consts[each][0], tctx.consts[each][1]+1, False]
            for each in tctx.procs:
                ctx.procs[each] = tctx.procs[each]
            pbuf = copy.deepcopy(buf)
            buf = copy.deepcopy(ctx.procs[ir.args])
            # 此处我的理解是sp不用变换
            ir_eval(buf, ctx)
            for each in tctx.vars:
                # 在下一层修改了一个全局变量
                if each in ctx.vars and ctx.vars[each][1] == tctx.vars[each][1]+1 and ctx.vars[each][2] == True:
                    tctx.vars[each] = [tctx.vars[each][0], tctx.vars[each][1], True]
                # 在下一层定义了与全局变量同名的局部变量，在下一层没有修改全局变量，在下一层去掉了这个变量
                else:
                    continue
            ctx = copy.deepcopy(tctx)
            # 常量不可以变化，把之前的弄回来就好
            # procs都用之前的就好
            for index in range(0, len(buf)):
                print(index, end=' ')
                print(buf[index])
            buf = copy.deepcopy(pbuf)

        elif ir.op == IrOpCode.Halt: # 怎么判断啥时候halt？
            break

        else:
            raise RuntimeError('invalid instruction')
        

# parser = Parser(Lexer(TEST_PROGRAM))
# prog = parser.program()
# buf = []
# prog.gen(buf)
# for index in range(0, len(buf)):
#     print(index, end=' ')
#     print(buf[index])
# ctx = EvalContext({}, {}, {})
# ir_eval(buf, ctx)

parser = Parser(Lexer(TEST_PROGRAM))
prog = parser.program()
ctx = EvalContext({}, {}, {})
prog.eval(ctx)

# 只有在assign的时候会修改变量
# 数据结构改变涉及到的操作有：loadvar,store,defvar,deflit,defproc,halt,call
# DefLit/DefProc/DefVar已修改,
# 发现了，在运算的时候，还是涉及到操作数的问题？
# 决定了，不在halt里修改东西，而是在call里一网打尽

# eval里修改的函数有：assign/const/var/procedure/call,


