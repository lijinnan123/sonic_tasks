package ast;

import error.MyException;
import headers.EvalContext;

public class Program extends ASTNodeImpl{
    Block block;
    public Program(Block block){
        this.block = block;
    }

    @Override
    public void eval(EvalContext ctx) throws MyException {
        this.block.eval(ctx);
    }
}
