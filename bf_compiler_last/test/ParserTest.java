package test;

import ast.ASTOut;
import ast.Program;
import compiler.Lexer;
import compiler.Parser;
import error.MyException;
import headers.EvalContext;
import headers.Ir;

import java.util.ArrayList;

public class ParserTest {
    public static void eval_test(String str) throws MyException {
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
    public static void gen_test(String str) throws MyException {
        Lexer lx = new Lexer(str);
        Parser parser = new Parser(lx);
        try {
            Program pro = parser.program();
            ASTOut.astout(pro);
            EvalContext ctx = new EvalContext();
            ArrayList<Ir> buf = new ArrayList<Ir>();
            pro.gen(buf);
            for(int i=0; i<buf.size(); i++){
                System.out.println(buf.get(i).getOp());
            }
            parser.ir_eval(buf, ctx);
        }catch (MyException e){
            System.out.println("error: " + e.getMessage());
        }
    }

    public static void main(String[] args) throws MyException {
        String str;
        str = "+++++++[>++++++++++<-]>++.\n" +
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
        str = "<.";
        str = "++;+";
        str = "-.";
        ParserTest.eval_test(str);
        ParserTest.gen_test(str);
    }
}
