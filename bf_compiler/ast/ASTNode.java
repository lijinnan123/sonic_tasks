package ast;

import error.MyException;
import headers.EvalContext;

public interface ASTNode {
    void eval(EvalContext ctx) throws MyException;
    public void gen();
}
