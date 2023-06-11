package ast;

public class ASTOut {
    static public void astout(ASTNode node){
        if(node instanceof Program){
            astout(((Program) node).block);
        }else if (node instanceof Block){
            for(int i=0; i<((Block) node).exprs.size(); i++){
                astout(((Block) node).exprs.get(i));
            }
        }else if (node instanceof LoopExpr){
            astout(((LoopExpr) node).block);
        }else if (node instanceof NonLoopExpr){
            System.out.println(((NonLoopExpr) node).getToken());
        }
    }
}
