static_assert(0, "include node not properly implemented")
static_assert(0, "include node not properly implemented")


bool ExpandTheMacro() {
    std::cout << "Congrats! You included the thing!" << std::endl;
    return 1;
}
// Macro POTATO with args None expanding to '12345'
// Macro FOO with args None expanding to '12345 > 4578'

int main() {
    int x = 3;
    int sum = 0;

    for(int i = 0; i < x; i++) {
        sum += i;
    }
    if (1) {
        return sum;
    } else {
        return -1;
    }
}
