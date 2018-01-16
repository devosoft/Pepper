#define includeguard

int main() {

#ifdef includeguard
    std::cout << "Lookit, we're defined!" << std::endl;
#else
    std::cout << "Oh no, we're not defined!" << std::endl;
#endif
}
