#include <iostream>
#include <string>
#include <algorithm>
#include <fstream>
#include <string.h>
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
#include <sstream>
/* OpenSSL headers */
#include "openssl/bio.h"
#include "openssl/ssl.h"
#include "openssl/err.h"

struct clargs {
    std::string server;
    int port;
    bool pop3s = false; //-T
    bool stls = false; //-S
    std::string certfile;
    std::string certaddr;
    bool new_only = false;
    bool del = false; //delete
    std::string auth_file;
    std::string out_dir;
};

int main(int argc, char *argv[]);