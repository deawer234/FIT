<?php 

#################################
#   Function checks arguments   #
################################# 
function checkArguments()
{
    global $argc;

    global $recursive;
    global $parse_script; 
    global $int_script;
    global $parse_only;
    global $int_only;
    global $xam;
    global $dir;

    $options = getopt(null, ["help", "directory:","recursive", "parse-script:","int-script:","parse-only", "int-only", "jexamxml:" ]);
    if ( array_key_exists("help", $options))
    {
        if ( $argc == 2)
        {
            fprintf(STDOUT, "Skript (test.php v jazyku PHP 7.4) \n bude slúžiť pre automatické testovanie postupnej aplikácie \n parse.php a interpret.py. Skrip prejde \n zadaný adresár s testami a využije ich pre \n otestovanie spravnej funkčnosti oboch programov \n vrátane vygenerovania prehľadného súhrnu v HTML 5 do STDOUT. \n ");
            exit(OK);
        }
        else 
        {
            exit(ERR_WRONG_PARAMS);
        }
        
    }
    if ($argc > 1 && $argc < 10)
    {
        if (array_key_exists("directory", $options))
        {
            $dir = $options["directory"];
            if ( file_exists($dir) == false )
            {
                exit (ERR_OPEN_INPUT_FILE);
            }
        }
        if (array_key_exists("recursive", $options))
        {
            $recursive = true;
        }
        if (array_key_exists("parse-script", $options))
        {
            $parse_script=$options["parse-script"];
            if ( file_exists($parse_script) == false )
            {
                exit (ERR_OPEN_INPUT_FILE);
            }
        }
        if (array_key_exists("int-script", $options))
        {
            $int_script=$options["int-script"];
            if ( file_exists($int_script) == false )
            {
                exit (ERR_OPEN_INPUT_FILE);
            }
        }
        if (array_key_exists("parse-only", $options))
        {
            if ((array_key_exists("int-only", $options)  || array_key_exists("int-script", $options)))
            {
                exit (ERR_WRONG_PARAMS);
            }
            else 
            {
                $int_only = false;
            }
            
        }
        if (array_key_exists("int-only", $options))
        {
           if ((array_key_exists("parse-only", $options)  || array_key_exists("parse-script", $options)))
            {
               exit (ERR_WRONG_PARAMS);
            }
            else 
            {
                $parse_only = false ;
            }
        }
        if (array_key_exists("jexamxml",$options))
        {
            $xam = $options["jexamxml"];
            if ( file_exists($xam) == false )
            {
                exit (ERR_OPEN_INPUT_FILE);
            }
        }
        return; 
    }
    return; 
}
?>