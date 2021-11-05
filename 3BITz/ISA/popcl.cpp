
#include "popcl.hpp"
#include "err.hpp"


using namespace std;

BIO* bio;
string response;

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

bool load_ca(SSL_CTX *ctx, string certfile, string certaddr){
    if(certfile != ""){
        if(!SSL_CTX_load_verify_locations(ctx, certfile.c_str(), NULL)){
            return false;
        }
    }
    else if(certaddr != ""){
        if(!SSL_CTX_load_verify_locations(ctx, NULL, certaddr.c_str())){
            return false;
        }
    }else{
        SSL_CTX_set_default_verify_paths(ctx);  
    }
}

bool response_ok(){
    char* buff;
    buff = new char[1024];
    memset(buff, 0, 1024);
    if(BIO_read(bio, buff, 1024) == 0){
        return false;
    }
    response.clear();
    response = buff;
    delete[] buff;
    //cout << response;
    if(response.substr(0, 3) == "+OK"){
        return true;
    }else{
        return false;
    }
}


//Otevře připojení
int connect_to_server(string server, int port){
    string connstr = server + ":" + to_string(port);
    bio = BIO_new_connect(connstr.c_str());
    if(!bio){
        cerr << "Invalid hostname or port\n";
        return -1;
    }

    if(BIO_do_connect(bio) <= 0)
    {
        cerr << "Connection failed\n";
        return -1;
    }
    return response_ok();
}

int connect_to_server_secured(string server, int port, string certfile, string certaddr){
    SSL_CTX *ctx;
    //const SSL_METHOD *method = ;
    ctx = SSL_CTX_new(SSLv23_client_method());
    if(ctx == nullptr){
        return 0;
    }
    load_ca(ctx, certfile, certaddr);
    
    bio = BIO_new_ssl_connect(ctx);
    SSL *ssl;
    BIO_get_ssl(bio, &ssl);
    SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
    string connstr = server + ":" + to_string(port);
    BIO_set_conn_hostname(bio, connstr.c_str());
    if(BIO_do_connect(bio) <= 0)
    {
        cout << "Nepodařilo se připojit k serveru\n";
        return SERVER_CONNECTION_ERR;
    }
    if(SSL_get_verify_result(ssl) != X509_V_OK)
    {
        cout << "Nepodařilo se potrdit certifikáty\n";
        return CERT_ERR;
    }
    return response_ok();
}


bool send_command(string command){
    if(BIO_write(bio,command.c_str(),command.length()) <= 0){
        cerr << "Nepodařilo se odeslat zprávu server\n";
        return false;
    }
    return true;
}

int login(string authfile){
    string username, password;
    ifstream file(authfile.c_str());
    if(!file.is_open()){
        cerr << "Nepodařilo se otevřit soubor s přihlačovacími údaji\n";
        return FILE_READ_ERR;
    }
    getline(file, username);
    send_command("USER " + username.substr(username.find(" = ") + 3, username.length()) + "\r\n");
    if(!response_ok()){
        cerr << "Neplatné uživatelské jméno nebo heslo\n";
        file.close();
        return -1; // invalid username or password
    }
    getline(file, password);
    send_command("PASS " + password.substr(password.find(" = ") + 3, password.length()) + "\r\n");
    if(!response_ok()){
        cerr << "Neplatné uživatelské jméno nebo heslo\n";
        file.close();
        return -1; // invalid username or password
    }
    file.close();
    return 0;
}

bool is_message_new(string out, string inmessage){
    struct dirent *entry = nullptr;
    DIR *dp = nullptr;

    dp = opendir(out.c_str());
    if (dp != nullptr) {
        while ((entry = readdir(dp)))
            if(!strcmp(entry->d_name, inmessage.c_str())){
                closedir(dp);
                return false;
            }
    }

    closedir(dp);
    return true;;
}

int process_message(string out, bool news, bool del){
    int enumber = 0;
    if(response != "")
        enumber = stoi(response.substr(response.find(" ") + 1, response.find(" ", 5) - 4));
    if(!del && !news){
        mkdir(out.c_str(), 0700);
        for(int i = 0; i < enumber; i++)
        {
            if(!send_command("RETR " + to_string(i + 1) + "\r\n")){
                cout << "hello\n";
                return SERVER_COMMUNICATION_ERR;
            }
            string filename;
            if(response_ok()){
                smatch id;
                regex regex("[M|m]essage-[I|i][D|d]:.*");
                regex_search(response, id, regex);
                filename = id.str();
                filename = filename.substr(12, filename.length());
                ofstream file(out + "/" + filename + ".txt");
                if(response.at(response.length() - 3) == '.'){
                    response.erase(response.length() - 3, 3);
                    file << response;
                    file.close();
                }else{
                    file << response;
                    file.close();
                    response_ok();
                }
            }
        }
        cout << "Staženo " + to_string(enumber) + " zpráv\n";
    }else if(del && !news){ //Pokud byl zadán pouze argument -d, odešle příkaz ke smazání všech zpráv na serveru
        for(int i = 0; i < enumber; i++)
        {
            send_command("DELE " + to_string(i + 1) + "\r\n");
            response_ok();
        }
    }else if(!del && news){ //Pokud byl zadán pouze argument -n, zkontroluje všechny zprávy na serveru a porovná je s již uloženými zprávami, pokud její id ješět v není v out složce, stáhne tuto zprávu
        int newnum = 0;
        mkdir(out.c_str(), 0700);
        for(int i = 0; i < enumber; i++)
        {
            send_command("RETR " + to_string(i + 1) + "\r\n");
            string filename;
            if(response_ok()){
                smatch id;
                regex regex("[M|m]essage-[I|i][D|d]:.*");
                regex_search(response, id, regex);
                filename = id.str();
                filename = filename.substr(12, filename.length());
                if(is_message_new(out, filename + ".txt")){
                    ofstream file(out + "/" + filename + ".txt");
                    if(response.at(response.length() - 3) == '.'){
                        response.erase(response.length() - 3, 3);
                        file << response;
                        file.close();
                    }else{
                        file << response;
                        file.close();   
                        response_ok();
                    }
                    newnum++;
                }
            }
        }
        if(newnum == 0){
            cout << "Schránka neobsahuje žádné nové zprávy\n";
        }else{
            cout << "Staženo " + to_string(newnum) + " nových zpráv\n";
        }
    }
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

    if(args.pop3s){
        connect_to_server_secured(args.server,args.port, args.certfile, args.certaddr);
    }else{
        connect_to_server(args.server, args.port);
    }
    if(args.stls){
        send_command("STLS\r\n"); //STLS connection TODO
        response_ok();

    }
    if((err = login(args.auth_file))!= 0){
        return err;
    }


    send_command("STAT\r\n");
    response_ok();

    if(args.del){

    }

    process_message(args.out_dir, args.new_only, args.del);

    send_command("QUIT\r\n");
    response_ok();
    return 0;
}



