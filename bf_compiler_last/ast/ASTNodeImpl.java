package ast;

import error.MyException;
import headers.EvalContext;
import headers.Ir;

import java.util.ArrayList;

public abstract class ASTNodeImpl implements ASTNode{
    public void eval(EvalContext ctx) throws MyException {

    }
    public void gen(ArrayList<Ir> buf) throws MyException{

    }
}
