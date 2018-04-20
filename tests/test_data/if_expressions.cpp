#if 2 + 1 - 2 + 100
"tested 2 + 2 - 2 + 100" ;
#endif

#if 0 || 1
"tested 0 || 1";
#endif

#if 2 + 2 * 2
"tested 2 + 2 * 2";
#endif

#if (2 + 2) * 2
"tested (2 + 2) *2";
#endif

#if 2 >> 1
"tested 2 >> 1";
#endif

#if ~2
"tested ~2";
#endif

#if 2 & 2
"tested 2 & 2";
#endif

#if 2 && 2
"tested 2 && 2";
#endif

#if 2 >> 1 - 1 || 'a'
"tested 2 >> 1 - 1 || 'a'";
#endif

#if 100 % 100 + 2
"tested 100 % 100 + 2";
#endif

#if 3 | 3
"tested 3 | 3";
#endif

#if 'a' ^ 'b'
"tested 'a' ^ 'b'";
#endif

#if !0
"tested !0";
#endif

#if 2 + 2 - 4 < 1
"tested 2 + 2 - 4 < 1";
#endif

#if 1 > (2 + 2 - 4)
"tested 1 > (2 + 2 - 4)";
#endif

#if 1 == (1 + 0)
"tested 1 == (1 + 0)"
#endif

#if 'b' >= 'b'
"tested 'b' >= 'b'";
#endif

#if 'a' <= 'b'
"tested 'a' <= 'b'";
#endif

#if 'a' == 97
"tested 'a' == 97";
#endif

#if 'a' != 98
"tested 'a' != 98";
#endif

#if 2 << 1
"tested 2 << 1 ";
#endif

#if 2 > 0? 2 : 0
"tested 2>0? 2 : 0";
#endif