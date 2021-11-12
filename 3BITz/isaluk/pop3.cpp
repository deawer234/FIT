/**
 * VUT FIT - ISA - 2020
 * Klient POP3 s podporou TLS
 * Havlíček Lukáš - xhavli53
 */


#include "pop3.hpp"

Pop3::Pop3(string server, string port, bool n_is_on)
{
    SSL_load_error_strings();
    ERR_load_BIO_strings();
    OpenSSL_add_all_algorithms();
    SSL_library_init();
    p_server = server;
    p_port = atoi(port.c_str());
    p_n_is_on = n_is_on; 
}

/**
 * @brief Změnění původně nastaveného portu
 * 
 * @param port Nový port 
 */
void Pop3::change_port(string port){
    p_port = atoi(port.c_str());
}

/**
 * @brief Šifrované (pop3s) připojení k serveru
 */
int Pop3::secure_connect_server(){
    SSL_CTX* ctx;
    ctx = SSL_CTX_new(SSLv23_client_method());
    SSL_CTX_set_default_verify_paths(ctx);
    bio = BIO_new_ssl_connect(ctx);
    SSL_CTX_free(ctx);
    BIO_get_ssl(bio, &ssl);
    SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);


    string hostname_message = p_server + ":" + to_string(p_port);
    BIO_set_conn_hostname(bio, hostname_message.c_str());


    if(BIO_do_connect(bio) <= 0)
    {
        cout << "problem1" << endl;
    }

    if(SSL_get_verify_result(ssl) != X509_V_OK)
    {
        cout << "Nepodařilo se ověřit certifikát" << endl;
    }

    return 0;
}

/**
 * @brief Nešifrované připojení k serveru
 */
int Pop3::connect_server(){
    
    string host_name = p_server + ":" + to_string(p_port); 
    bio = BIO_new_connect(host_name.c_str());
    if(bio == NULL)
    {
        cout << "help" << endl;
    }

    if(BIO_do_connect(bio) <= 0)
    {
        cout << "help" << endl;   
    }

    return 0;
}

/**
 * @brief Získání odpovědi ze serveru
 * 
 * @return Opověď ze serveru
 */
string Pop3::get_server_response(){
    char buf [1024];
    memset(buf, 0, 1024);
    auto len = BIO_read(bio, buf, 1024);
    if(len == 0)
    {
        cout<<"fuck2"<<endl;
    }
    else if(len < 0)
    {
    if(! BIO_should_retry(bio))
        {
            cout<<"fuck"<<endl;
        }
            cout<<"fuck1"<<endl;
    }
    return buf;
}

/**
 * @brief Posílání zprávy na server
 * 
 * @param message Zpráva k odeslání 
 */
void Pop3::write_to_server(string message){
    if(BIO_write(bio, message.c_str(), message.length()) <= 0)
    {
        if(! BIO_should_retry(bio))
        {
            cout << "Error" << endl;
        }
        cout << "Retry" << endl;
    }
}

/**
 * @brief Autentifikace uživatele
 * 
 * @param user přihlašovací jméno
 * @param password přihlašovací heslo
 */
void Pop3::authorization(string user, string password){
    string user_message = "USER " + user + "\r\n";
    string password_message = "PASS " + password + "\r\n";
    
    write_to_server(user_message);
    get_server_response();
    write_to_server(password_message);
    get_server_response();
}

/**
 * @brief Stahování zpráv ze serveru
 * 
 * @param out_dir výstupní adresář
 */
void Pop3::download_server_messages(string out_dir){
    string retr;
    string name_of_file;
    bool file_is_already_downloaded = false;
    list<string> downloaded_files;
    
    DIR *dir;
    struct dirent *entry;
    // struct stat info;

    dir = opendir(out_dir.c_str()); //Otevírání výstupního adresáře
    if(!dir){   //Adresář nenalezen 
        int check = mkdir(out_dir.c_str(), 0700);   //Vytvoření adresáře
        if(check){
            cout << "Unable to reate directory" << endl; //TODO error
        }
    }else{
        if(p_n_is_on){  //Pracování s novýma zprávama
            while((entry = readdir(dir)) != NULL){
                if(entry->d_name[0] != '.'){
                    downloaded_files.push_front(entry->d_name); //Ukládání názvů již stažených emailů do listu
                }
            }
        }
    }
    closedir(dir);  //zavření výstupního adresáře
    get_number_of_messages();   //Získání počtu zpráv na serveru
    for(int i = 1; i <= p_number_of_messages; i++){
        retr = "RETR " + to_string(i) + "\r\n"; 
        // retr = "RETR 901\r\n"; 
        write_to_server(retr);

        string response = get_server_response();
        while (1)   //Získávání zprávy, dokud není +OK
        {
            if(check_response_message(response)){   //Kontrola správnosti zprávy
                if(!check_end_of_message(response)){
                    response += get_server_response();

                }else{
                    break;
                }
            }else{
                response = get_server_response();
            }
        }
        string id = get_id(response, i);   //Získání id z emailu
        string name = out_dir + "/" + id + ".txt";
        
        if(p_n_is_on){  //Pracování s novýma zprávama
            for(auto name:downloaded_files){
                if(contains_id(name, id)){  //Zjiťování, jestli id nové zprávy, neni mezi stáhnutýma zprávama
                    file_is_already_downloaded = true;
                }
            }
        }
        
        if(!file_is_already_downloaded){    //Vytvořená nového souboru pro zprávu, která ještě nebyla stáhnutá
            count_of_downloaded_messages++;
            name_of_file = name;
            ofstream outfile (name_of_file);
            outfile << parse_message(response); //Vepsání zprávy do souboru
            outfile.close();    //Zavření souboru
        }else{
            new_messages = true;
        }
        file_is_already_downloaded = false;
        
    }
}

/**
 * @brief Mazání zpráv ze serveru
 * 
 */
void Pop3::delete_messages(){
    string dele;
    get_number_of_messages();
    for(int i = 1; i <= p_number_of_messages; i++){ //Posílání Delete příkazu pro jednotlivé zprávy
        dele = "DELE " + to_string(i) + "\r\n";
        write_to_server(dele);
        get_server_response();
    }
}

/**
 * @brief Získání počtu zpráv na serveru
 * 
 */
void Pop3::get_number_of_messages(){
    if(p_number_of_messages == -1){
        string list = "STAT\r\n";

        write_to_server(list);
        string server_response = get_server_response();
        string tmp = server_response.substr(4);
        size_t pom = tmp.find(" ");
        tmp = tmp.substr(0, pom);
        p_number_of_messages = atoi(tmp.c_str());
    }
}

/**
 * @brief Odpojení ze serveru
 * 
 */
void Pop3::quit_server(){
    string quit_message = "QUIT\r\n"; 
    write_to_server(quit_message);
}

/**
 * @brief uzavření spojení
 * 
 */
void Pop3::close_connection(){
    //SSL_CTX_free(ctx);
    //BIO_reset(bio);
    BIO_free_all(bio);
}



/**
 * @brief Kontrola ceritfíkátů
 * 
 * @param is_certfile flag, zda byl zadání soubor s certifikátem
 * @param is_certaddr flag, zda byl zadání adresář s certifikátem
 * @param certfile soubor s certifikátem
 * @param ceraddr adresář s certifikátem
 */
// void Pop3::check_certificates(string certfile, string ceraddr){
//     if(certfile != ""){
//         if(! SSL_CTX_load_verify_locations(ctx, certfile.c_str(), NULL))
//         {
//             cout << "cough" <<endl;
//         }
//     }else if(ceraddr != ""){
//         if(! SSL_CTX_load_verify_locations(ctx, NULL, ceraddr.c_str()))
//         {
//             cout << "cough" <<endl;
//         }
//     }else{
//         SSL_CTX_set_default_verify_paths(ctx);
//     }
// }

/**
 * @brief Konstrola konce zprávy
 * 
 * @param message zpráva
 * @return true obsahuje "\r\n.\r\n"
 * @return false neobsahuje "\r\n.\r\n"
 */
bool Pop3::check_end_of_message(string message){
    if(message.find("\r\n.\r\n") != string::npos){
        return true;
    }
    return false;
}

/**
 * @brief Kontrola správnosti zprávy ze serveru
 * 
 * @param message zpráva
 * @return true zpráva je v pořádku
 * @return false zpráva není v pořádku
 */
bool Pop3::check_response_message(string message){
    if ((message.find("+OK") != string::npos) || (message.find("Received:") != string::npos)) {
        return true;
    }
    return false;
}


/**
 * @brief Odeslání STLS zprávy na server 
 * 
 */
void Pop3::stls_message(){
    string stls_message = "STLS \r\n";
    write_to_server(stls_message);
}

/**
 * @brief Přechod na šifrované zabezpečení
 * 
 */
void Pop3::upgrade(){
    SSL_CTX* ctx;
    ctx = SSL_CTX_new(SSLv23_client_method());
    SSL_CTX_set_default_verify_paths(ctx);
    
    BIO *ret = NULL, *sslc = NULL;

    sslc = BIO_new_ssl(ctx, 1);
    SSL_CTX_free(ctx);
    ret = BIO_push(sslc, bio);

    BIO_get_ssl(ret, &ssl);

    if(BIO_do_connect(ret) <= 0)
    {
        cout << "problem1" << endl;
    }
    if(SSL_get_verify_result(ssl) != X509_V_OK)
    {
        cout << "Nepodařilo se ověřit certifikát" << endl;
    }

    bio = ret;
}

/**
 * @brief Konstrola, jestli zpráva osahuje stejné id
 * 
 * @param message zpráva
 * @param id id pro porovnání
 * @return true zpráva obsahuje id
 * @return false zpráva neobsahuje id
 */
bool Pop3::contains_id(string message, string id){
    if (message.find(id) != string::npos) {
        return true;
    }
    return false;
}

/**
 * @brief Získání id ze zprávy od serveru
 * 
 * @param message zpráva
 * @return string id ze zprávy
 */
string Pop3::get_id(string message, int number_of_message){
    smatch tmp;
    string id;
    regex regex("[M|m]essage-[I|i][D|d]:(\\s?)+<.*>");
    if(regex_search(message, tmp, regex)){
        id = tmp.str();
        id = id.substr(12);
        size_t pos_start = id.find("<");
        size_t pos_end = id.find(">");
        id = id.substr(pos_start + 1);
        id = id.substr(0, pos_end - 1);

        std::replace( id.begin(), id.end(), '/', '_'); // replace all '/' to '_'
    }else{
        id = "mesage_" + to_string(number_of_message);
    }
    

    return id;
}

/**
 * @brief Upravení zprávy k výpisu
 * 
 * @param message zpráva
 * @return string upravená zpráva k výpisu
 */
string Pop3::parse_message(string message){
    string new_message;

    //Odstranění +OK části zprávy
    if(message[0] == '+'){  
        size_t end_of_line = message.find("\n");
        new_message = message.erase(0, end_of_line + 1);
    }else{
        new_message = message;
    }
    
    //Odstranění přebytečného konce zprávy
    if(check_end_of_message(new_message)){
        size_t end_of_message = new_message.find("\r\n.\r\n");
        new_message = new_message.erase(end_of_message,5);
    }else if((message.find(".\r\n") != string::npos)){
        size_t end_of_message = new_message.find(".\r\n");
        new_message = new_message.erase(end_of_message,3);
    }

    return new_message;
}

/**
 * @brief Výpis o počtu stažených zpráv
 * 
 */
void Pop3::write_number_of_downloaded_messages(){
    if(new_messages){   //Staženy nové zprávy
        cout << "Staženy " + to_string(count_of_downloaded_messages) + " nové zprávy" << endl;
    }else{
        cout << "Staženo " + to_string(count_of_downloaded_messages) + " zpráv" << endl;
    }
}