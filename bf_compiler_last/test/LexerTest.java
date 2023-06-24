package test;

import compiler.Lexer;
import error.MyException;
import headers.Header.Token;

public class LexerTest {
    public static void main(String[] args){
        String hello_word = "+++++++[>++++++++++<-]>++.";
        Lexer lx = new Lexer(hello_word);
        while(!lx.eof()){
            try{
                Token t = lx.next();
                System.out.println(t.getValue());
            }catch (MyException e){
                System.out.println("error: "+e.getMessage());
            }
        }
    }
}
