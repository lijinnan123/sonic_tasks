package ast;

import error.MyException;
import headers.EvalContext;
import headers.Ir;
import java.util.ArrayList;

public interface ASTNode {
    void eval(EvalContext ctx) throws MyException;
    public void gen(ArrayList<Ir> buf) throws MyException;
}
