/**
 * VUT FIT - ISA - 2020
 * Klient POP3 s podporou TLS
 * Havlíček Lukáš - xhavli53
 */

//g++ popcl.cpp -o popcl
//./popcl
// powershell -> New-NetFirewallRule -DisplayName "WSL" -Direction Inbound  -InterfaceAlias "vEthernet (WSL)"  -Action Allow 
//./popcl ping "$(hostname).local" -p 110 -a user.txt -o smh
//./popcl server -p port -T -S -c certfile -C certaddr -d -n -a authFile -o outFile 
// pop3.seznam.cz
#include "popcl.hpp"


//Struktura se zadanýma argumentama
struct argumetns_info{
    string server, port, certfile, certaddr, auth_file, out_dir, username, password;
    bool t_is_on, s_is_on, d_is_on, n_is_on = false;
}ar;

int main(int argc, char **argv) {
    parse_arguments(argc, argv);
    check_compulsory_arguments();
    read_authentication_file();
    Pop3 pop3 = Pop3(ar.server, ar.port, ar.n_is_on);

    //Šifrovaná komunkace (pop3s)
    if(ar.t_is_on == true){
        if(ar.port.length() == 0){
            pop3.change_port("995");
        }

        //pop3.check_certificates(ar.certfile, ar.certaddr);
        pop3.secure_connect_server();
        pop3.get_server_response();
    }else if(ar.s_is_on == true){ //RFC 2595
        if(ar.port.length() == 0){
            pop3.change_port("110");
        }

        pop3.connect_server();
        pop3.get_server_response();
        pop3.stls_message();
        pop3.get_server_response();
        //pop3.check_certificates(ar.certfile, ar.certaddr);
        pop3.upgrade();
    }else{  //Nešifrovaná komunikace
        if(ar.port.length() == 0){
            pop3.change_port("110");
        }

        pop3.connect_server();
        pop3.get_server_response();
    }

    pop3.authorization(ar.username, ar.password);

    if(ar.d_is_on){ //Mazání zpráv
        pop3.delete_messages();
        pop3.quit_server();
        pop3.close_connection();
    }else{
        pop3.download_server_messages(ar.out_dir);
        pop3.quit_server();
        pop3.get_server_response();
        pop3.close_connection();
        pop3.write_number_of_downloaded_messages();
    }

    return 0;
}

/**
 * @brief Parsování argumentů a ukládání do struktury
 * 
 * @param argc počet argumentů
 * @param argv argumenty
 */
void parse_arguments(int argc, char **argv){
    //Kontrola minimálního počtu argumentů 
    if(argc < 2){
        help();
        exit(0);
    }

    if(argv[1] == "--help"){
        help();
        exit(0);
    }

    check_other_arguments(argv[1]); //Kontrola argumentu serveru
    ar.server = argv[1];

    //Parsování argumentů
    for(int i = 2; i < argc ; i++){
        if(string(argv[i]) == "-p"){
            check_other_arguments(argv[++i]);
            ar.port = argv[i];
        }else if(string(argv[i]) == "-T"){
            ar.t_is_on = true;
        }else if(string(argv[i]) == "-S"){
            ar.s_is_on = true;
        }else if(string(argv[i]) == "-c"){
            check_other_arguments(argv[++i]);
            ar.certfile = argv[i];
        }else if(string(argv[i]) == "-C"){
            check_other_arguments(argv[++i]);
            ar.certaddr = argv[i];
        }else if(string(argv[i]) == "-d"){
            ar.d_is_on = true;
        }else if(string(argv[i]) == "-n"){
            ar.n_is_on = true;
        }else if(string(argv[i]) == "-a"){
            check_other_arguments(argv[++i]);
            ar.auth_file = argv[i];
        }else if(string(argv[i]) == "-o"){
            check_other_arguments(argv[++i]);
            ar.out_dir = argv[i];
        }
    }
}

/**
 * @brief Kontrola, zda např. na místě argumentu <certfile> není jiný argument
 * 
 * @param argv argument
 */
void check_other_arguments(string argv){
    if(argv == "-p" || argv == "-T" || argv == "-S" || argv == "-c" || argv == "-C" || argv == "-d" || argv == "-n" || argv == "-a" || argv == "-o"){
        help();
        exit(0);
    }
}

/**
 * @brief Kontrola, jestli jsou zadány povinné argumenty
 * 
 */
void check_compulsory_arguments(){
    if(ar.server.length() == 0 || ar.auth_file.length() == 0 || ar.out_dir.length() == 0){
        help();
        exit(0);
    }
}

/**
 * @brief Zprcování <auth_file> souboru
 * 
 */
void read_authentication_file(){
    string txt;
    string username_text = "username = ";
    string password_text = "password = ";
    // Čtení ze souboru 
    ifstream authentication_file(ar.auth_file);

    int line_counter = 0;
    // Čtení souboru po řádcích
    while (getline (authentication_file, txt)) {
        if (line_counter == 0){
            ar.username = txt.substr(username_text.length());
        }else if(line_counter == 1){
            ar.password = txt.substr(password_text.length());
        }
        line_counter++;
    }

    // Zavření souboru
    authentication_file.close();
}

/**
 * @brief Výpis používání programu
 * 
 */
void help(){
    cout << "Klient POP3 s podporou TLS" << endl << endl;
    cout << "Použití:" << endl;
    cout << "popcl <server> [-p <port>] [-T|-S [-c <certfile>] [-C <certaddr>]] [-d] [-n] -a <auth_file> -o <out_dir>" << endl << endl;
    cout << "Paratmetry: "<< endl;
    cout << "<server>       --povinný parametr, IP adresa, nebo doménové jméno požadovaného zdroje." << endl;
    cout << "-p <port>      --volitelný parametr, -p specifikuje číslo portu <port> na serveru" << endl;
    cout << "-T             --volitelný parametr, zapíná šifrování celé komunikace (pop3s), pokud není parametr uveden použije se nešifrovaná varianta protokolu" << endl;
    cout << "-S             --volitelný parametr, naváže nešifrované spojení se serverem a pomocí příkazu STLS (RFC 2595) přejde na šifrovanou variantu protokolu" << endl;
    cout << "-c <certfile>  --volitelný parametr, -c definuje soubor <certfile> s certifikáty, který se použije pro ověření platnosti certifikátu SSL/TLS předloženého serverem (použití jen s parametrem -T, nebo -S)." << endl;
    cout << "-C <certaddr>  --volitelný parametr, -C určuje adresář <certaddr>, ve kterém se mají vyhledávat certifikáty, které se použijí pro ověření platnosti certifikátu SSL/TLS předloženého serverem. (Použití jen s parametrem -T, nebo -S)." << endl;
    cout << "-d             --volitelný parametr, zašle serveru příkaz pro smazání zpráv" << endl;
    cout << "-n             --volitelný parametr, pracuje se pouze s novými zprávami. " << endl;
    cout << "-a <auth_file> --povinný parametr, vynucuje autentizaci (příkaz USER), obsah konfiguračního souboru <auth_file> je zobrazený níže." << endl;
    cout << "-o <out_dir>   --povinný parametr,  specifikuje výstupní adresář <out_dir>, do kterého má program stažené zprávy uložit." << endl;
}