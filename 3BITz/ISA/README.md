# POP3 klient s podporou TLS
# Autor: Daniel Němec, xnemec92@stud.fit.vutbr.cz
# Datum: 14.11.2021

# Popis:
  Program slouží ke stažení elektronické pošty přes POP3 protokol. Při zadání pouze povinných parametrů
  stáhne do určené složky zprávy ze serveru. Počet stažených zpráv vypíše na výstup. 
  Dalšími parametry lze tuto základní funkcionalitu měnit.

# Spuštění:
  $ ./popcl <server> [-p <port>] [-T|-S [-c <certfile>] [-C <certaddr>]] [-d] [-n] -a <auth_file> -o <out_dir>

# Překlad:
  $ make         - přeložení projektu
  $ make clean   - smazání přeloženého projektu
  $ make tar     - vytvoření archivu tar

# Seznam souborů:
    Makefile
    README
    popcl.cpp
    popcl.hpp
    pop3.cpp
    pop3.hpp
    err.hpp
    manual.pdf