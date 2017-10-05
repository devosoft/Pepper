#define POTATOS=8

#py [pepper.POTATOS += 1 for i in range(0, 10)]
#py print('There are {} potatos'.format(pepper.POTATOS)) 

#include <iostream>

int main() {
    std::cout << "Hello world" << std::endl;
    std::cout << "There are " << POTATOS << " potatos" << std::endl;
}

