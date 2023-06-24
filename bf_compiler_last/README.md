# Brainfuck编译器
## 自定义语法
```agsl
Program = Block EOF
Block = Exprs
Exprs = [NonLoopExpr+LoopExpr+]+
LoopExpr = Block
```
其中，EOF为词法分析之后，在结尾追加的EOF符号。
## 项目环境
使用idea工具，在windows下，用jdk11编译。
## 运行方法
运行LexerTest.java或ParserTest.java中的主函数，可以在各自的str处修改输入。

