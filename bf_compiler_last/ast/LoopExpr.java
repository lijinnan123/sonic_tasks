package ast;

import error.MyException;
import headers.EvalContext;
import headers.Ir;

import java.util.ArrayList;
import headers.Header.IrOpCode;

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
    // 这段逻辑要反复看
    public void gen(ArrayList<Ir> buf) throws MyException {
        ArrayList<Ir> innerbuf = new ArrayList<Ir>();
        this.block.gen(innerbuf);
        buf.add(new Ir(IrOpCode.JUMP, innerbuf));
    }
}
