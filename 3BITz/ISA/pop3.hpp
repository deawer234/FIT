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
#include <sys/stat.h>
#include <sstream>
#include <regex>
#include "err.hpp"
/* OpenSSL headers */
#include "openssl/bio.h"
#include "openssl/ssl.h"
#include "openssl/err.h"

class pop3{
    private:
        BIO *bio;
        bool new_messages = false;
        bool del = false;
        bool pop3s = false;
        bool stls = false;
        bool retron = false;
        bool reading = false;
        std::string response;
        std::string outdir;
        std::string server;
        std::string authfile;
        std::string certfile;
        std::string certaddr;
        
        int port;
        //Privátní funkce
        bool response_ok();
        bool load_ca(SSL_CTX *ctx);
        bool is_message_new(std::string message);
        bool end_of_message(std::string message);
        bool retrieve_messages(int num);
        std::string read();
    public:
        pop3(const struct clargs &args);
        ~pop3();
        int connect_to_server();
        int connect_to_server_secured();
        void send_command(std::string command);
        void process_message();
        void login();
        void init_stls();
        void quit();
        
};