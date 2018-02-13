#define add_these_plz(a, b) a + b

bool isEven(int x) {
    return x % 2;
}

int main() {
    cout << "whoa, let's add some things" << endl;
    cout << add_these_plz(1, 2) << endl;
    cout << "I wonder if they're even?" << endl;
    cout << add_these_plz(1+2, 3) << endl;
    cout << isEven(add_these_plz(1, 2)) << endl;
}