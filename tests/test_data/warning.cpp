#define __M__ 0

#if defined(__M__) || defined(__X__)
#warning "WARN"
#endif

#ifdef __M__
#warning "WARN"
#endif

int main()
{

    return 0;
}