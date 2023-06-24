package headers;

public class Header {
    public enum Token {
        INCREMENT("Increment"),
        DECREASE("Decrease"),
        MOVE_NEXT("MoveNext"),
        MOVE_PREV("MovePrev"),
        INPUT("Input"),
        OUTPUT("Output"),
        LOOP_OPEN("LoopOpen"),
        LOOP_CLOSE("LoopClose"),
        EOF("EOF");

        private final String value;

        private Token(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }
    public enum NodeType{
        TapeCell,
        Tape
    }

    public enum IrOpCode{
        ADD,
        SUB,
        NEXT,
        PREV,
        INPUT,
        OUTPUT,
        JUMP,
    }
}