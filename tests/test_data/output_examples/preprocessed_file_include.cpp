static_assert(false, "include node not properly implemented")
// Macro POTATO with args None expanding to '12345'
// Macro FOO with args None expanding to '12345 > 4578'

int main() {
    int x = 3;
    int sum = 0;

    for(int i = 0; i < x; i++) {
        sum += i;
    }
    return sum;
}
