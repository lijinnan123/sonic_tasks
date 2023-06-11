package headers;

import java.util.ArrayList;

import error.MyException;

public class EvalContext {
    private ArrayList<Integer> tapecell = new ArrayList<>();
    private int index;
    public EvalContext(){
        // this.type = type;
        this.tapecell.add(0);
        this.index = 0;
    }

    public Integer getTapecell() {
        return tapecell.get(this.index);
    }

    public void setTapecell(Integer a)  throws MyException {
        if(this.tapecell.size() - 1 < this.index){
            this.tapecell.add(a);
        } else if (a < 0 || a > 127) {
            throw new MyException("纸带每格数字超过0-127范围");
        } else{
            this.tapecell.set(this.index, a);
        }
    }

    public int getIndex() {
        return index;
    }

    public void setIndex(int index) throws MyException{
        if(index < 0){
            throw new MyException("纸带范围不能为负数");
        }
        else if (index >= this.tapecell.size()){
            tapecell.add(0);
        }
        this.index = index;
    }
}
