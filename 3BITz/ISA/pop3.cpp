

#include "popcl.hpp"

using namespace std;

//Konstruktor třídy
pop3::pop3(const clargs &arguments){
    SSL_load_error_strings();
    ERR_load_BIO_strings();
    OpenSSL_add_all_algorithms();
    SSL_library_init();

    this->server = arguments.server;
    this->port = arguments.port;
    this->authfile = arguments.auth_file;
    this->certfile = arguments.certfile;
    this->certaddr = arguments.certaddr;
    this->outdir = arguments.out_dir;
    this->del = arguments.del;
    this->new_messages = arguments.new_only;
    this->pop3s = arguments.pop3s;
    this->stls = arguments.stls;
}

//Destruktor
pop3::~pop3(){
    BIO_free_all(bio);
};

//Error handler
void throw_error(string err_message, int err_num){
    cerr << err_message << endl;
    exit(err_num);
}

/*
*   Metoda načte zadané certifikáty, pokud nebyly certifikáty zadány, načte defaultně uložené certifikáty.
*/
bool pop3::load_ca(SSL_CTX *ctx){
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
    return true;
}

/*
*   Metoda hledá konec zprávy ze serveru.
*/
bool pop3::end_of_message(string message){
    size_t pos = string::npos;
    

    return true;
}

/*
*   Metoda posílá serveru příkaz RETR num.
*/
bool pop3::retrieve_messages(int num){
    bool retval = false;
    retron = true;
    send_command("RETR " + to_string(num + 1) + "\r\n");
    retval = response_ok();
    retron = false;
    return retval;
}

/*
*   Metoda čeká na celou zprávu ze serveru.
*   Po přijetí zprávy ji uloží do proměnné response a ukládá pořád, dokud nenajde konec zprávy.
*   Nakonec vyhodnotí zda se nejedná o error.
*/
bool pop3::response_ok(){
    string reply;
    size_t pos;
    response.clear();
    char *buff = NULL;
    buff = new char[1024];
    while(1){
        //memset(buff, '\0', 1024); 
        //cout << "helo\n";
        auto len = BIO_read(bio, buff, 1024);
        buff[len] = '\0';
        reply += buff;

        if(retron){
            if(reply.find("\r\n.\r\n") != string::npos){
                break;
            }
        }
        else{
            if(reply.find_last_of("\r\n") != string::npos){
                break;
            }
        }
        //reading = end_of_message(reply);
        //reply = read();
        
    }
    response = reply;
    delete[] buff;
    //if(!retron)
    //    cout << response.substr(0, response.find_first_of('\n'));
    //cout << response << endl;
    if(response.substr(0, 3) == "+OK"){
        return true;
    }else{
        return false;
    }
}

string pop3::read(){
    
    
    
    //if(BIO_read(bio, buff, 1024) == 0){
    //    throw_error("Nepodařilo se získat odpověď ze serveru", SERVER_COMMUNICATION_ERR);
    //}

    return "";
}


/*
*   Metoda otevře nešifrované připojení.
*/
int pop3::connect_to_server(){
    string connstr = server + ":" + to_string(port);
    bio = BIO_new_connect(connstr.c_str());
    if(!bio){
        throw_error("Nesprávný hostname nebo port", SERVER_CONNECTION_ERR);
    }

    if(BIO_do_connect(bio) <= 0)
    {
        throw_error("Připojení se nezdařilo", SERVER_CONNECTION_ERR);
    }
    return response_ok();
}


/*
*   Metoda naváže šifrované připojení pop3s k serveru.
*   Načte certifikaty a po připojení následně certifikáty zkontroluje.
*/
int pop3::connect_to_server_secured(){
    SSL_CTX *ctx;

    ctx = SSL_CTX_new(SSLv23_client_method());
    if(ctx == nullptr){
        throw_error("Nelze načíst certifikáty", CERT_ERR);
    }
    if(!load_ca(ctx)){
        throw_error("Nepodařilo se načíst certifikáty", CERT_ERR);
    }
    
    bio = BIO_new_ssl_connect(ctx);
    SSL_CTX_free(ctx);
    SSL *ssl;
    BIO_get_ssl(bio, &ssl);
    SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);

    string connstr = server + ":" + to_string(port);

    BIO_set_conn_hostname(bio, connstr.c_str());

    if(BIO_do_connect(bio) <= 0)
    {
        throw_error("Připojení se nezdařilo", SERVER_CONNECTION_ERR);
    }
    if(SSL_get_verify_result(ssl) != X509_V_OK)
    {
        throw_error("Nepodařilo se potrdit certifikáty", CERT_ERR);
    }
    return response_ok();
}

/*
*   Metoda odešle příkaz serveru
*/
void pop3::send_command(string command){
    if(BIO_write(bio,command.c_str(),command.length()) <= 0){
        throw_error("Nepodařilo se odeslat zprávu serveru", SERVER_COMMUNICATION_ERR);
    }
}

/*
*   Metoda zahajuje přihlašování k serveru pomocí přihlašovacích údajů ze souboru
*/
void pop3::login(){
    string username, password;
    ifstream file(authfile.c_str());
    if(!file.is_open()){
        throw_error("Nepodařilo se otevřít soubor s přihlačovacími údaji", FILE_READ_ERR);
    }

    getline(file, username);
    send_command("USER " + username.substr(username.find(" = ") + 3, username.length()) + "\r\n");
    if(!response_ok()){
        file.close();
        throw_error("Neplatné uživatelské jméno nebo heslo", AUTH_ERR);
    }

    getline(file, password);
    send_command("PASS " + password.substr(password.find(" = ") + 3, password.length()) + "\r\n");
    if(!response_ok()){
        file.close();
        throw_error("Neplatné uživatelské jméno nebo heslo", AUTH_ERR);
    }
    file.close();
}

/*
*   Metoda porovná id zpráv, a rozhodne zda je zpráva již stažena.
*   Načte si obsah složky a porovnává názvy souborů s id přijaté zprávy.
*/
bool pop3::is_message_new(string inmessage){
    struct dirent *entry = nullptr;
    DIR *dp = nullptr;

    dp = opendir(outdir.c_str());
    if (dp != nullptr) {
        inmessage = inmessage.substr(inmessage.find_first_of('<') + 1, inmessage.length());
        while ((entry = readdir(dp))){
            if(!strcmp(entry->d_name, inmessage.c_str())){
                closedir(dp);
                return false;
            }
        }
    }
    cout << response << endl;
    closedir(dp);
    return true;
}

/*
*   Metoda na stažení nebo smazání zpráv podle zadaných argumentů.
*   Nejdříve zjistí kolik je ve schránce zpráv, poté se pokusí zprávy stáhnout/smazat pomocí příkazů RETR num a DELE num.
*   Při stahování také maže ukončovací tečku zpráv.
*/
void pop3::process_message(){
    send_command("STAT\r\n");
    response_ok();
    int enumber = 0;
    if(response != ""){
        enumber = stoi(response.substr(response.find(" ") + 1, response.find(" ", 5) - 4));
    }
    if(enumber == 0){
        cout << "Schránka neobsahuje žádné zprávy\n";
    }else{
        if(!del){
            int newnum = 0;
            mkdir(outdir.c_str(), 0700);
            for(int i = 0; i < enumber; i++)
            {
                retrieve_messages(i);
                string filename;
                smatch id;
                regex reg("[M|m]essage-[I|i][D|d]:(\\s?)+<.*>");
                regex_search(response, id, reg);
                filename = id.str();

                if(filename == ""){
                    regex re("[M|m]essage-[I|i][D|d]:(\\s?)+<.*>");
                    regex_search(response, id, re);
                    filename = "email_" + to_string(i+1);
                }else{
                    filename = filename.substr(filename.find_first_of('<') + 1, filename.length());
                    filename.erase(filename.find_first_of('>'), 1);
                }

                size_t pos;
                while((pos = filename.find('/')) != string::npos){
                    filename.replace(pos, 1, "a");
                }
                

                if(!new_messages || (new_messages && is_message_new(filename + ".eml"))){
                    ofstream file(outdir + "/" + filename + ".eml");
                    response.erase(response.length()-3, 3);
                    response.erase(0, response.find_first_of("\r\n") + 2);
                    file << response;
                    newnum++;
                }
            }
            if(new_messages){
                if(newnum == 0){
                    cout << "Schránka neobsahuje žádné nové zprávy\n";
                }else{
                    cout << "Staženo " + to_string(newnum) + " nových zpráv\n";
                }
            }else{
                cout << "Staženo " + to_string(enumber) + " zpráv\n";
            }
        }else{ //Pokud byl zadán pouze argument -d, odešle příkaz ke smazání všech zpráv na serveru
            for(int i = 0; i < enumber; i++)
            {
                send_command("DELE " + to_string(i + 1) + "\r\n");
                if(!response_ok()){
                    throw_error("Zpráva k vymazání neexistuje", SERVER_COMMUNICATION_ERR);
                }
            }
            cout << "Obsah schránky byl vymazán" << endl;
        }
    }
}

/*
*   Metoda zašle serveru příkaz quit pro ukončení spojení.
*/
void pop3::quit(){
    send_command("QUIT\r\n");
    response_ok();
}

/*
*   Metoda zahájí šiforvané spojení pomocí stls.
*   Načte certifikáty a vylepší nezabezpečené připojení na šifrované.
*/
void pop3::init_stls(){
    send_command("STLS\r\n");
    response_ok();

    SSL_CTX *ctx;
    ctx = SSL_CTX_new(SSLv23_client_method());
    if(ctx == nullptr){
        throw_error("Nelze načíst certifikáty", CERT_ERR);
    }
    if(!load_ca(ctx)){
        throw_error("Nepodařilo se načíst certifikáty", CERT_ERR);
    }

    BIO *ret, *sslc = NULL;
    sslc = BIO_new_ssl(ctx, 1);
    SSL_CTX_free(ctx);
    ret = BIO_push(sslc, bio);
    SSL *ssl;
    BIO_get_ssl(ret, &ssl);

    if(BIO_do_connect(ret) <= 0){
        throw_error("Připojení se nezdařilo", SERVER_CONNECTION_ERR);
    }
    bio = ret;
    if(SSL_get_verify_result(ssl) != X509_V_OK)
    {
        throw_error("Nepodařilo se potrdit certifikáty", CERT_ERR);
    }
}
