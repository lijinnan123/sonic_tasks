package headers;

import headers.Header.IrOpCode;

import java.util.ArrayList;

public class Ir {
    public IrOpCode getOp() {
        return this.op;
    }

    public void setOp(IrOpCode op) {
        this.op = op;
    }

    public ArrayList<Ir> getIr() {
        return this.ir;
    }

    public void setIr(ArrayList<Ir> ir) {
        this.ir = ir;
    }

    private IrOpCode op;
    private ArrayList<Ir> ir;

    public Ir(IrOpCode op, ArrayList<Ir> ir){
        this.op = op;
        this.ir = ir;
    }
}
