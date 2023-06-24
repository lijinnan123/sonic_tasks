package ast;

import error.MyException;
import headers.EvalContext;
import headers.Ir;
import java.util.ArrayList;

public class Block extends ASTNodeImpl{
    ArrayList<ASTNode> exprs;
    public Block(ArrayList<ASTNode> ASTNodes){
        this.exprs = ASTNodes;
    }
    public void eval(EvalContext ctx) throws MyException {
        for(int i=0; i<this.exprs.size(); i++){
            this.exprs.get(i).eval(ctx);
        }
    }
    public void gen(ArrayList<Ir> buf) throws MyException {
        for(int i=0; i<this.exprs.size(); i++){
            this.exprs.get(i).gen(buf);
        }
    }
}
