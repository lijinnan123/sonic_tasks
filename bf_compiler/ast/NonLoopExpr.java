package ast;

import java.util.Scanner;

import error.MyException;
import headers.EvalContext;
import headers.Header.Token;

public class NonLoopExpr extends ASTNodeImpl {
    private Token token;

    public Token getToken(){
        return this.token;
    }
    public NonLoopExpr(Token token){
        this.token = token;
    }
    public void eval(EvalContext ctx) throws MyException {
        switch(this.token.getValue()){
            case "Increment":
                ctx.setTapecell(ctx.getTapecell()+1);
                break;
            case "Decrease":
                ctx.setTapecell(ctx.getTapecell()-1);
                break;
            case "MoveNext":
                ctx.setIndex(ctx.getIndex()+1);
                break;
            case "MovePrev":
                ctx.setIndex(ctx.getIndex()-1);
                break;
            case "Input":
            {
                Scanner scanner = new Scanner(System.in);

                System.out.println("Enter an integer: ");
                int inputInteger = scanner.nextInt();

                scanner.close();
                ctx.setTapecell(inputInteger);
                break;
            }
            case "Output":
            {
                Integer a = ctx.getTapecell();
                char ch = (char)a.intValue();
                System.out.print(ch);
                break;
            }
            default:

        }
    }
}
