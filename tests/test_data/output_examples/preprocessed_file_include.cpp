static_assert(false, "include node not properly implemented")

int main() {
    int x = 3;
    int sum = 0;

    for(int i = 0; i < x; i++) {
        sum += i;
    }
    return sum;
}