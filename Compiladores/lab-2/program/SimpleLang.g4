grammar SimpleLang;

prog: stat+ ;

stat: expr NEWLINE ;

expr
    // multiplicación, división y módulo
    : expr op=('*' | '/' | '%') expr      # MulDivMod
    // suma y resta
    | expr op=('+' | '-') expr            # AddSub
    // potencia
    | expr op='^' expr                    # Pow
    // átomos
    | INT                                 # Int
    | FLOAT                               # Float
    | STRING                              # String
    | BOOL                                # Bool
    | '(' expr ')'                        # Parens
    ;

INT    : [0-9]+ ;
FLOAT  : [0-9]+'.'[0-9]* ;
STRING : '"' .*? '"' ;
BOOL   : 'true' | 'false' ;
NEWLINE: '\r'? '\n' ;
WS     : [ \t]+ -> skip ;
