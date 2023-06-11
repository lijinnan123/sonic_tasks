package compiler;

import ast.*;
import error.MyException;
import headers.Header.Token;

import java.util.ArrayList;

import ast.ASTNode;
import ast.NonLoopExpr;

public class Parser {
    private Lexer lx;
    public Parser(Lexer lexer){
        this.lx = lexer;
    }
    public boolean check(String str){
        int p = this.lx.getP();
        Token token = this.lx.next();
        this.lx.setP(p);
        if(token.getValue() == str){
            return true;
        }
        return false;
    }

    public void expect(String str) throws MyException{
        //下一个token必须是啥
        if(this.check(str)){
            this.lx.next();
        }
        else {
            throw new MyException("next token must be "+str);
        }
    }
    public Program program() throws MyException{
        Block block = this.block();
        this.expect("EOF");
        return new Program(block);
    }
    public Block block() throws MyException{
        ArrayList<ASTNode> ASTNodes = new ArrayList<>();
        while(!this.check("EOF")){
            if(this.check("Increment")
                    || this.check("Decrease")
                    || this.check("MoveNext")
                    || this.check("MovePrev")
                    || this.check("Input")
                    || this.check("Output")){
                ASTNodes.add(this.nonLoopExpr());//next在嵌套里面了
            } else if (this.check("LoopOpen")) {
                this.lx.next();
                LoopExpr le = this.loopExpr();
                ASTNodes.add(le);
            } else if (this.check("LoopClose")) {
                this.lx.next();
                break;
            } else{
                //raise error, 语法上括号不成对，就要报错
                throw new MyException("括号不成对");
            }
        }
        return new Block(ASTNodes);
    }
    public LoopExpr loopExpr() throws MyException{
        Block block = this.block();
        return new LoopExpr(block);
    }

    public NonLoopExpr nonLoopExpr(){
        Token next = this.lx.next();
        NonLoopExpr ret = new NonLoopExpr(next);
        return ret;
    }
}
