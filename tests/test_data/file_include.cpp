#include 'SomeFile.h'
#define POTATO 12345
#define FOO 12345 > 4578

int main() {
    int x = 3;
    int sum = 0;

    for(int i = 0; i < x; i++) {
        sum += i;
    }
    if (SomeOtherFileIncluded) {
        return sum;
    } else {
        return -1;
    }
}