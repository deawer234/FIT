popcl : popcl.o 
	g++ -std=gnu++11 -Wall -Wextra -o popcl popcl.o -lcrypto -lssl

popcl.o : popcl.cpp popcl.hpp
	g++ -std=gnu++11 -Wall -Wextra -c -o popcl.o popcl.cpp

clean:
	rm *.o popcl xnemec92.tar
