#include "popcl.hpp"
#include "err.hpp"

using namespace std;

//Parsování argumentů z příkazové řádky pomocí std::find
char* get_option(char ** begin, char ** end, const std::string & option)
{
    char ** itr = std::find(begin, end, option);
    if (itr != end && ++itr != end)
    {
        return *itr;
    }
    return 0;
}

int main(int argc, char* argv[]){
    struct clargs args;
    int server;
    char* port;
    int err = 0;

    if (argc < 2){
        return -1;
    }else{
        args.server = argv[1];
    }

    char* authfile = get_option(argv, argv + argc, "-a");
    if(!authfile){
        std::cout << "no auth"<< std::endl;  // no auth
        return -1;
    }
    args.auth_file = authfile;
    char* outdir = get_option(argv, argv + argc, "-o");
    if(!outdir){
        std::cout << "no out"<< std::endl;  // no out
        return -1;
    }
    args.out_dir = outdir;
    args.port = 110;

    for(int i = 1; i < argc;i++){
        if(argv[i][0] == '-'){
            switch(argv[i][1]){
                case 'p':
                    port = get_option(argv, argv + argc, "-p");
                    if(atoi(port) <= 0){
                        return -1;
                    }
                    args.port = atoi(port);
                    break;
                case 'T':
                    args.pop3s = true;
                    break;
                case 'S':
                    args.stls = true;
                    break;
                case 'c':
                    args.certfile = get_option(argv, argv + argc, "-c");
                    break;
                case 'C':
                    args.certaddr = get_option(argv, argv + argc, "-C");
                    break;
                case 'd':
                    args.del = true;
                    break;
                case 'n':
                    args.new_only = true;
                    break;
            }
        }
    }
    pop3 pop3c(args);

    if(args.pop3s){
        pop3c.connect_to_server_secured();
    }else{
        pop3c.connect_to_server();
    }
    if(args.stls){
        pop3c.init_stls();
    }
    pop3c.login();
    pop3c.process_message();
    pop3c.quit();
    return 0;
}




