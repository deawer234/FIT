#include "popcl.hpp"
#include "err.hpp"
#include <getopt.h>

void print_help(){
    std::cout << "Klient POP3 s podporou TLS" << '\n';
    std::cout << "Použití:" << '\n';
    std::cout << "-h              - zobrazí napovědu" << '\n';
    std::cout << "popcl <server> [-p <port>] [-T|-S [-c <certfile>]" << '\n';
    std::cout << "[-C <certaddr>]] [-d] [-n] -a <auth_file> -o <out_dir>" << '\n';
    std::cout << "server          - povinný parametr (IP adresa nebo doménové jméno)" << '\n';
    std::cout << "-p <port>       - specifikuje číslo portu na serveru" << '\n';
    std::cout << "-T              - zapéna šifrovaní" << '\n';
    std::cout << "-S              - naváže nešifrovane spojení se serverem a pomoci příkazu" << '\n';
    std::cout << "                  STLS přejde na šifrovanou verzi protokolu" << '\n';
    std::cout << "-c <certfile>   - definuje soubor s certifikaty" << '\n';
    std::cout << "-C <certaddr>   - definuje adresář ve kterem se mají vyhledávat certifikaty" << '\n';
    std::cout << "-d              - stáhne a smaže zprávy" << '\n';
    std::cout << "-n              - stáhnou se nové zprávy" << '\n';
    std::cout << "-a <auth_file>  - povinny parametr, specifikuje soubor s přihlašovacími údaji" << '\n';
    std::cout << "-o <out_dir>    - povinny parametr, specifikuje výstupní adresář" << '\n';
}

int main(int argc, char* argv[]){
    struct clargs args;
    
    if (argc < 2){
        print_help();
        return -1;
    }else{
        args.server = argv[1];
    }

    //Parsování parametrů pomocí getopt
    for(;;)
    {
        switch(getopt(argc, argv, ":p:TSc:C:dna:o:"))
        {
            case 'p':
                args.port = atoi(optarg);
            continue;

            case 'T':
                args.pop3s = true;
            continue;

            case 'S':
                args.stls = true;
            continue;

            case 'c':
                args.certfile = optarg;
            continue;

            case 'C':
                args.certaddr = optarg;
            continue;

            case 'd':
                args.del = true;
            continue;

            case 'n':
                args.new_only = true;
            continue;

            case 'a':
                args.auth_file = optarg;
            continue;

            case 'o':
                args.out_dir = optarg;
            continue;

            case '?':
            case 'h':
                print_help();
                return 0;

            default:
            break;
        }
    break;
    }

    if(args.auth_file == ""){
        std::cout << "Nebyl zadán soubor s přihlašovacími údaji\n\n";
        print_help();
        return 0;
    }
    if(args.out_dir == ""){
        std::cout << "Nebyla zadána složka pro výstup\n\n";
        print_help();
        return 0;
    }
    if(args.server == ""){
        std::cout << "Nebyl zadán server\n\n";
        print_help();
        return 0;
    }

    //Nastavení výchozích portů, pokud nebyl zadán parametr -p
    if(args.port == -1 && args.pop3s)
        args.port = 995;
    if(args.port == -1 && !args.pop3s)
        args.port = 110;

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




