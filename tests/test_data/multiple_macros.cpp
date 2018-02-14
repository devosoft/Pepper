#define FINALMACRO "this is the last macro"
#define SECONDMACRO std::cout << FINALMACRO << std::endl;
#define FIRSTMACRO SECONDMACRO

int main() {
    std::cout << "We're going to expand some nested macros (oh no)" << std::endl;
    FIRSTMACRO;
}