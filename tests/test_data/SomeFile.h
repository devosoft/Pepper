#define SomeFileIncluded true
#define SomeFileMultilineIncluded true

bool ExpandTheMacro() {
    std::cout << "Congrats! You included the thing!" << std::endl;
    return SomeFileIncluded;
}