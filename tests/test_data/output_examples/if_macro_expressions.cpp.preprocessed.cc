// Macro M1 with args None expanding to '2'
// Macro M2 with args None expanding to ''a''
// Macro M3 with args None expanding to '2 - 2'
// Macro M5 with args ['a', 'b', 'c'] expanding to 'a + b + c'
// Macro M7 with args None expanding to '0 || ('a' - 97 + 1) || 1'
// Macro M8 with args None expanding to ''a' == 97'
// Macro M9 with args ['a', 'b'] expanding to 'a / b'
// Macro M10 with args ['a', 'b', 'c', 'd'] expanding to 'a+b > c+d? a+c : b + d'
// if expression result: 1
"testing call M1 - M1 + 1";
// endif expression 

// if expression result: 12
"testing call M5 resulting in 0 + 0 + 12";
// endif expression 

// if expression result: 1
"testing call M3 or M1";
// endif expression 

// if expression result: 2
"testing M6 call + 2";
// endif expression 

// if expression result: 1
"tested defined call M4";
// endif expression 

// if expression result: -61
"tested defined(Not) * 122 - 123 / 2 ";
// endif expression 

// if expression result: 1
"testing call M7 && M8";
// endif expression 

// if expression result: 1
"testing call M9, evaluating to 3 / 2 ";
// endif expression 

// if expression result: 3
"testing call M10 with args 0, 1, 1, 2"
// endif expression 
