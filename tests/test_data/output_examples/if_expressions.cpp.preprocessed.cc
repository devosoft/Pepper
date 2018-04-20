// if expression result: 101
"tested 2 + 2 - 2 + 100" ;
// endif expression 

// if expression result: 1
"tested 0 || 1";
// endif expression 

// if expression result: 6
"tested 2 + 2 * 2";
// endif expression 

// if expression result: 8
"tested (2 + 2) *2";
// endif expression 

// if expression result: 1
"tested 2 >> 1";
// endif expression 

// if expression result: -3
"tested ~2";
// endif expression 

// if expression result: 2
"tested 2 & 2";
// endif expression 

// if expression result: 1
"tested 2 && 2";
// endif expression 

// if expression result: 1
"tested 2 >> 1 - 1 || 'a'";
// endif expression 

// if expression result: 2
"tested 100 % 100 + 2";
// endif expression 

// if expression result: 3
"tested 3 | 3";
// endif expression 

// if expression result: 3
"tested 'a' ^ 'b'";
// endif expression 

// if expression result: 1
"tested !0";
// endif expression 

// if expression result: 1
"tested 2 + 2 - 4 < 1";
// endif expression 

// if expression result: 1
"tested 1 > (2 + 2 - 4)";
// endif expression 

// if expression result: 1
"tested 1 == (1 + 0)"
// endif expression 

// if expression result: 1
"tested 'b' >= 'b'";
// endif expression 

// if expression result: 1
"tested 'a' <= 'b'";
// endif expression 

// if expression result: 1
"tested 'a' == 97";
// endif expression 

// if expression result: 1
"tested 'a' != 98";
// endif expression 

// if expression result: 4
"tested 2 << 1 ";
// endif expression 

// if expression result: 2
"tested 2>0? 2 : 0";
// endif expression 
