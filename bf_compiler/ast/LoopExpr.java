package ast;

import error.MyException;
import headers.EvalContext;

public class LoopExpr extends ASTNodeImpl {
    Block block;
    public LoopExpr(Block block){
        this.block = block;
    }
    public void eval(EvalContext ctx) throws MyException {
        while(ctx.getTapecell() != 0){
            this.block.eval(ctx);
        }
    }
}
