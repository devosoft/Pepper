#define __M__ 0

#if defined(__M__) || defined(__X__)
#warning "WARNING"
#endif

#ifdef __M__
#warning "WARNING"
#endif

int main()
{

    return 0;
}