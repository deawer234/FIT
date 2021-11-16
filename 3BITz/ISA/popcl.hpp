#include "pop3.hpp"

struct clargs {
    std::string server;
    int port = -1;
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
void print_help();