package ast;

import error.MyException;
import headers.EvalContext;
import headers.Ir;

import java.util.ArrayList;

public class Program extends ASTNodeImpl{
    Block block;
    public Program(Block block){
        this.block = block;
    }

    @Override
    public void eval(EvalContext ctx) throws MyException {
        this.block.eval(ctx);
    }
    public void gen(ArrayList<Ir> buf) throws MyException {
        this.block.gen(buf);
    }

}
