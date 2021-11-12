
popcl : popcl.o pop3.o
	g++ -std=gnu++11 -Wall -Wextra -o popcl popcl.o pop3.o -lcrypto -lssl

main.o : popcl.cpp popcl.hpp
	g++ -std=gnu++11 -Wall -Wextra -c -o popcl.o popcl.cpp

pop3.o : pop3.cpp pop3.hpp
	g++ -std=gnu++11 -Wall -Wextra -c -o pop3.o pop3.cpp