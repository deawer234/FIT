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
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <fstream>
#include <list>
#include <regex>

#include  "openssl/bio.h"
#include  "openssl/ssl.h"
#include  "openssl/err.h"

using namespace std;

class Pop3{
    public:
        Pop3(string server, string port, bool n_is_on);
        void change_port(string port);
        int connect_server();
        std::string get_server_response();
        void authorization(string user, string password);
        void download_server_messages(string out_dir);
        void quit_server();
        int secure_connect_server();
        void get_number_of_messages();
        void write_to_server(string message);
        void close_connection();
        void delete_messages();
        bool check_end_of_message(string message);
        void stls_message();
        //void check_certificates(string certfile, string ceraddr);
        bool check_response_message(string message);
        void upgrade();
        string parse_message(string message);
        bool contains_id(string message, string id);
        void write_number_of_downloaded_messages();
        string get_id(string message, int number_of_message);
        void clear_buffer();
        void delete_buffer();
    
    private:
        string p_server;
        int p_port;   
        bool p_n_is_on = false;
        BIO * bio;
        //SSL_CTX  *ctx = SSL_CTX_new(SSLv23_client_method());
        SSL  *ssl;
        int p_number_of_messages = -1;
        int count_of_downloaded_messages = 0;
        bool new_messages = false;
};