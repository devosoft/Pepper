#define M1 2
#define M2 'a'
#define M3 2 - 2
#define M4 M2 - 'c'
#define M5(a,b,c) a + b + c
#define M6 2 && M5(0,0,0)
#define M7 0 || ('a' - 97 + 1) || 1
#define M8 'a' == 97
#define M9(a,b) a / b

#if M1 - M1 + 1
"testing call M1 - M1 + 1";
#endif

#if M5(0, 0, 12)
"testing call M5 resulting in 0 + 0 + 12";
#endif

#if M3 || M1
"testing call M3 or M1";
#endif

#if M6 + 2
"testing M6 call + 2";
#endif

#if defined M4
"tested defined call M4";
#endif

#if defined(Not) * 122 - 123 / 2
"tested defined(Not) * 122 - 123 / 2 ";
#endif

#if M7 && M8
"testing call M7 && M8";
#endif

#if M9(3,2)
"testing call M9, evaluating to 3 / 2 ";
#endif