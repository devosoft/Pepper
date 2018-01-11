static_assert(false, "include node not properly implemented")
// Macro SomeFileIncluded with args None expanding to 'true'
// Macro SomeFileMultilineIncluded with args None expanding to 'true'

bool ExpandTheMacro() {
    std::cout << "Congrats! You included the thing!" << std::endl;
    return true;
}
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
