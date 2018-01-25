// Macro includeguard with args None expanding to 'true'

int main() {

// ifdef expression includeguard
    std::cout << "Lookit, we're defined!" << std::endl;
// endif expression 

// endif expression 

// endif expression 

// ifndef expression thisshouldabsolutelynotbedefined
    std::cout << "Lookit, the thing ISNT'T defined!" << std::endl;
// endif expression 
}
