#define __M__ 0

#if defined(__M__) || defined(__X__)
#warning "This warning should appear"
#endif


int main()
{

    return 0;
}