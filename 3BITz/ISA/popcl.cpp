
#include "popcl.hpp"
#include "err.hpp"


using namespace std;
BIO* bio;

//Parsování argumentů z příkazové řádky pomocí std::find
char* getOption(char ** begin, char ** end, const std::string & option)
{
    char ** itr = std::find(begin, end, option);
    if (itr != end && ++itr != end)
    {
        return *itr;
    }
    return 0;
}

bool loadCA(SSL_CTX *ctx, string certfile, string certaddr){
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

bool responseOk(){
    char* buff;
    buff = new char[1024];
    memset(buff, 0, 1024);
    if(BIO_read(bio, buff, 1024) == 0){
        return "";
    }
    string response = buff;
    delete[] buff;
    cout << response;
    if(response.substr(0, 3) == "+OK"){
        return true;
    }else{
        return false;
    }
}


//Otevře připojení
int connectToServer(string server, int port){
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
    return responseOk();
    
    // string buffer = "USER test2@mail.local\r\n";
    // write(sock, buffer.c_str(), buffer.length());

    // buff = new char[1024];
    // memset(buff, 0, 1024); // vyprazdneni bufferu
    // read(sock, buff, 1024);
    // cout << buff;

    // buffer = "PASS 12345\r\n";
    // write(sock, buffer.c_str(), buffer.length());

    // buff = new char[1024];
    // memset(buff, 0, 1024); // vyprazdneni bufferu
    // read(sock, buff, 1024);
    // cout << buff;

    // buffer = "STAT\r\n";
    // write(sock, buffer.c_str(), buffer.length());

    // buff = new char[1024];
    // memset(buff, 0, 1024); // vyprazdneni bufferu
    // read(sock, buff, 1024);
    // cout << buff;
    // stringstream helo;
    // for(int i = 1; i < 6; i++){
    //     helo << "RETR " << i << "\r\n";
    //     write(sock, helo.str().c_str(), helo.str().length());
    //     buff = new char[1024];
    //     memset(buff, 0, 1024); // vyprazdneni bufferu
    //     read(sock, buff, 1024);
    //     cout << buff;
    //     cout << helo.str() << endl;
    //     helo.str(string());
    // }

}

int connectToServerSecured(string server, int port, string certfile, string certaddr){
    SSL_CTX *ctx;
    //const SSL_METHOD *method = ;
    ctx = SSL_CTX_new(SSLv23_client_method());
    if(ctx == nullptr){
        return 0;
    }
    loadCA(ctx, certfile, certaddr);
    
    bio = BIO_new_ssl_connect(ctx);
    SSL *ssl;
    BIO_get_ssl(bio, &ssl);
    SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
    string connstr = server + ":" + to_string(port);
    BIO_set_conn_hostname(bio, connstr.c_str());
    if(BIO_do_connect(bio) <= 0)
    {
        cout << "failed conn\n";
        return -1;
    }
    if(SSL_get_verify_result(ssl) != X509_V_OK)
    {
        cout << "failed verify\n";
        return -1;
    }
    return responseOk();
}


bool sendCommand(string command){
    if(BIO_write(bio,command.c_str(),command.length()) <= 0){
        cerr << "Failed to send command to server\n";
        return false;
    }
    return true;
}

int login(string authfile){
    string username, password;
    ifstream file(authfile.c_str());
    if(!file.is_open()){
        cerr << "Failed to open authentification file\n";
        return FILE_READ_ERR;
    }
    getline(file, username);
    sendCommand("USER " + username.substr(username.find(" = ") + 3, username.length()) + "\r\n");
    if(!responseOk()){
        cerr << "Invalid username or password\n";
        return -1; // invalid username or password
    }
    getline(file, password);
    sendCommand("PASS " + password.substr(password.find(" = ") + 3, password.length()) + "\r\n");
    if(!responseOk()){
        cerr << "Invalid username or password\n";
        return -1; // invalid username or password
    }
    return 0;
}

bool processMails(string out, bool news, bool del){
    return true;
}

int main(int argc, char* argv[]){
    struct clargs args;
    int server;
    char* port;
    if (argc < 2){
        return -1;
    }else{
        args.server = argv[1];
    }

    char* authfile = getOption(argv, argv + argc, "-a");
    if(!authfile){
        std::cout << "no auth"<< std::endl;  // no auth
        return -1;
    }
    args.auth_file = authfile;
    char* outdir = getOption(argv, argv + argc, "-o");
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
                    port = getOption(argv, argv + argc, "-p");
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
                    args.certfile = getOption(argv, argv + argc, "-c");
                    break;
                case 'C':
                    args.certaddr = getOption(argv, argv + argc, "-C");
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
        connectToServerSecured(args.server,args.port, args.certfile, args.certaddr);
    }else{
        connectToServer(args.server, args.port);
    }
    if(args.stls){
        sendCommand("STLS\r\n");
        responseOk();

    }
    login(args.auth_file);
    sendCommand("CAPA USER\r\n");
    responseOk();


    
    return 0;
}



