package test;

import compiler.Lexer;
import headers.Header.Token;

public class LexerTest {
    public static void main(String[] args){
        String hello_word = "+++++++[>++++++++++<-]>++.";
        Lexer lx = new Lexer(hello_word);
        while(!lx.eof()){
            Token t = lx.next();
            System.out.println(t.getValue());
        }
    }
}
