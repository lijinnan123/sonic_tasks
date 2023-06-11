package test;

import ast.ASTOut;
import ast.Program;
import compiler.Lexer;
import compiler.Parser;
import error.MyException;
import headers.EvalContext;

public class ParserTest {
    public static void main(String[] args) throws MyException {
        String str = "+++++++[>++++++++++<-]>++.\n" +
                "<+++[>++++++++++<-]>-.\n" +
                "+++++++..\n" +
                "+++.\n" +
                ">+++[>++++++++++<-]>++.\n" +
                "<<<+++[>--------<-]>.\n" +
                "<+++[>++++++++<-]>.\n" +
                "+++.\n" +
                "------.\n" +
                "--------.\n" +
                ">>+.\n" +
                "      ";
//        String str = "-.";
        Lexer lx = new Lexer(str);
        Parser parser = new Parser(lx);
        try {
            Program pro = parser.program();
            ASTOut.astout(pro);
            EvalContext ctx = new EvalContext();
            pro.eval(ctx);
        }catch (MyException e){
            System.out.println("error: " + e.getMessage());
        }
    }
}
