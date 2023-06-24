package compiler;

import error.MyException;
import headers.Header.Token;

import java.util.ArrayList;

public class Lexer {
    private int p;
    //private ArrayList<Integer> s = new ArrayList<>();;
    private String s;

    public Lexer(String str) {
        this.p = 0;
        this.s = str;
        this.skip_blank();
    }

    public boolean eof(){
        return this.p >= this.s.length();

    }

    public int getP(){
        return this.p;
    }

    public void setP(int p){
        this.p = p;
    }

    public void skip_blank(){
        this.s = this.s.replaceAll("\\s+", "");
    }

    public Token next() throws MyException{
        if(this.eof()){
            return Token.EOF;
        }
        switch (this.s.charAt(this.p)){
            case '+':
                this.p += 1;
                return Token.INCREMENT;
            case '-':
                this.p += 1;
                return Token.DECREASE;
            case '>':
                this.p += 1;
                return Token.MOVE_NEXT;
            case '<':
                this.p += 1;
                return Token.MOVE_PREV;
            case '.':
                this.p += 1;
                return Token.OUTPUT;
            case ',':
                this.p += 1;
                return Token.INPUT;
            case '[':
                this.p += 1;
                return Token.LOOP_OPEN;
            case ']':
                this.p += 1;
                return Token.LOOP_CLOSE;
            default:
                throw new MyException("invalid token");
        }
    }
}
