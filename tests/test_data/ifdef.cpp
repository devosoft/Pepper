#define includeguard

int main() {

#ifdef includeguard
    std::cout << "Lookit, we're defined!" << std::endl;
#else
    std::cout << "Oh no, we're not defined!" << std::endl;
#endif

#ifdef thisshouldabsolutelynotbedefined
    std::cout << "This shouldn't be here." << std::endl;
#endif

#ifndef includeguard
    std::cout << "This shouldn't be here either." << std::endl;
#endif

#ifndef thisshouldabsolutelynotbedefined
    std::cout << "Lookit, the thing ISNT'T defined!" << std::endl;
#else
    std::cout << "Somehow the thing was defined--bad." << std::endl;
    static_assert(false);
#endif
}