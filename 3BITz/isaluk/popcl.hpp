/**
 * VUT FIT - ISA - 2020
 * Klient POP3 s podporou TLS
 * Havlíček Lukáš - xhavli53
 */


#include <iostream>
#include <iostream>
#include <string>
#include <algorithm>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/socket.h>

#include "pop3.hpp"

using namespace std;

void check_other_arguments(string argv);
void check_compulsory_arguments();
void parse_arguments(int argc, char **argv);
void read_authentication_file();
void help();
