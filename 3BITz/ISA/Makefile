CC=g++
CFLAGS=-std=gnu++11 -Wall -Wextra
PROJECT=popcl

all : $(PROJECT)

pop3.o : pop3.cpp pop3.hpp
	$(CC) $(CFLAGS) -c pop3.cpp -o pop3.o

$(PROJECT).o : $(PROJECT).cpp popcl.hpp
	$(CC) $(CFLAGS) -c $(PROJECT).cpp -o $(PROJECT).o

$(PROJECT) : $(PROJECT).o pop3.o
	$(CC) $(CFLAGS) $(PROJECT).o pop3.o -lcrypto -lssl -o $(PROJECT)

clean :
	rm -f $(PROJECT) *.o xnemec92.tar

clean-o :
	rm -f *.o

tar : clean
	tar -cvf xnemec92.tar pop3.cpp pop3.hpp popcl.cpp popcl.hpp Makefile err.hpp manual.pdf README