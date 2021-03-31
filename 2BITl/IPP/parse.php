<?php
ini_set('display_errors', 'stderr');
$xmlcode = [];
array_push($xmlcode, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
$filename = [];
$file;
$argvs = [];
$statcall = []; 

//Kontrola argumentů
if($argc > 1)
{
    if($argv[1] == "--help")
    {
        echo("\nSkript načte ze standardního vstupu zdrojový kód v IPPcode21, zkontroluje lexikální a syntaktickou správnost kódu a vypíše na standardní výstup XML reprezentaci.
        \nSkript pracuje s parametry: \n--help: Vypíše nápovědu.\n--stats=file: Vypíše do souboru file statistiky v parametrech umístěných za tímto --stats.\nStatistiky se vypisují po řádcích dle pořadí v parametrech s možností jejich opakování.
        \nJe-li uveden pouze parametr --stats bez upřesnění statistik k výpisu, bude výstupem prázdný soubor. 
        \nParametry statistik: \n--loc: Vypíše počet řádků s instrukcemi (nepočítají se prázdné řádky ani řádky obsahující pouze komentář ani úvodní řádek).\n--comments: Vypíše počet řádků, na kterých se vyskytoval komentář.\n--labes: Vypíše počet definovaných návěští (tj.unikátních možných cílů skoku).\n--jumps: Vypíše počet všech instrukcí návratů z volání a instrukcí pro skoky (souhrnně podmíněné/nepodmíněné skoky a volání)\n--fwjumps: Vypíše počet dopředných skoků\n--backjumps: Vypíše počet zpětných skoků\n--badjumps: Vypíše počet špatných skoků na neexistující návěští\n ");
        exit(0);
    }
    else if(substr($argv[1], 0, 8) == "--stats=")
    {
        array_push($statcall, $argv[1]);
        $filename = explode('=', $argv[1]);
        $file = fopen($filename[1], 'w');
    }
    else
    {
        exit(10);
    }   
}

$header = false;
$valid = false;
$index = 0;
$labelarray = [];
$jumparray = [];
// STATP
$loc = 0;
$comments = 0;
$labels = 0;
$jumps = 0;
$fwjumps = 0;
$backjumps = 0;
$badjumps = 0;
$lastlabel = 0;

//Lexikální a syntaktická analýza
while($line = fgets(STDIN))
{
    $argnmr = 0;
    // Odstranění komentáře z řádku, pokud nějaký obsahuje
    if(strpos($line, "#") !== false)
    {
        $comments++;
        if(strpos($line, "#") == 0){
            continue;
        }
        else if($line[strpos($line, "#") - 1] == ' ')
        {
            $line = substr($line, 0, strpos($line, "#") - 1);
        }
        $tmp = explode('#', $line);
        $line = $tmp[0];
    }
    //Přeskočí prázdné řádky
    if($line[0] == "\n")
    {
        continue;
    }
    // Zkontrolování headeru
    if(!$header)
    {
        $header_counter = 0;
        for($i = 0;$i < strlen($line);$i++){
            if($line[$header_counter] == ' ')
                $header_counter++;
        }
        if(substr($line, $header_counter, 10) == ".IPPcode21")
        {
            array_push($xmlcode, "<program language=\"IPPcode21\">");
            $header = true;
            continue;
        }
        else
        {
            exit(21);
        }
    }

    $keyword = explode(' ', trim($line, "\n"));
    $index = array_search("", $keyword);
    if($index !== false)
        unset($keyword[$index]);
    $loc++;
    switch(strtoupper($keyword[0]))
    {
        // <var><symb>
        case "NOT":
        case "TYPE":
        case "STRLEN":
        case "INT2CHAR":
        case "MOVE":
            if(count($keyword) !== 3)
            {
                exit(23);
            }
            array_push($xmlcode,"\t<instruction order=\"$loc\" opcode=\"$keyword[0]\">");
            $argnmr++;
            if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[1]))
            {
                array_push($xmlcode,"\t\t<arg$argnmr type=\"var\">$keyword[1]</arg$argnmr>");
                $argnmr++;
                if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[2]))
                {
                    array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[2]</arg$argnmr>");
                }
                else
                {
                    constant_check($keyword[2], $argnmr, $xmlcode);
                }
            } 
            else
            {
                exit(23);
            }
            array_push($xmlcode, "\t</instruction>");
            break;
        //<var>
        case "POPS":
        case "DEFVAR":
            if(count($keyword) !== 2)
            {
                exit(23);
            }
            array_push($xmlcode, "\t<instruction order=\"$loc\" opcode=\"$keyword[0]\">");
            $argnmr++;
            
            if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[1]))
            {
                array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[1]</arg$argnmr>\n\t</instruction>");
            }
            else
            {
                exit(23);
            }
            break;
        //<label>
        case "LABEL":
            if(preg_match('/[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[1])){
                array_push($labelarray, $keyword[1]);
            }else{
                exit(23);
            }
            $labels++;
        case "JUMP":
        case "CALL":
            if(count($keyword) !== 2)
            {
                exit(23);
            }
            if(strtoupper($keyword[0]) == "JUMP" || strtoupper($keyword[0]) == "CALL")
            {
                if(array_search($keyword[1], $labelarray) !== false)
                {
                    $pos = array_search($keyword[1], $labelarray);
                    if($pos < $loc)
                    {
                        $backjumps++;
                    }
                    else
                    {
                        array_push($jumparray, $keyword[1]);
                    }
                }
                else
                {
                    array_push($jumparray, $keyword[1]);
                }
                $jumps++;
            }
            if(count($keyword) !== 2)
            {
                exit(23);
            }
            if(strtoupper($keyword[0]) == "CALL")
            {
                $jumps++;
            }
            $keyword = array_slice($keyword, 0, 2);
            array_push($xmlcode, "\t<instruction order=\"$loc\" opcode=\"$keyword[0]\">");
            $argnmr++;
            if(preg_match('/\b[a-zA-Z_$&%*!?-][a-zA-Z_$&%*!?0-9-]*\b/', $keyword[1]))
            {
                if(preg_match('/[@\/\\\\]/', $keyword[1]))
                {
                    exit(23);
                }
                else
                {
                    array_push($xmlcode, "\t\t<arg$argnmr type=\"label\">$keyword[1]</arg$argnmr>\n\t</instruction>");
                }
            }
            else
            {
                exit(23);
            }
            break;
        //<var><symb1><symb2>
        case "ADD":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":
        case "GT":
        case "EQ":
        case "AND":
        case "OR":
        case "STRI2INT":
        case "CONCAT":
        case "GETCHAR":
        case "SETCHAR": 
            if(count($keyword) !== 4)
            {
                exit(23);
            }
            array_push($xmlcode, "\t<instruction order=\"$loc\" opcode=\"$keyword[0]\">");
            $argnmr++;
            if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[1]))
            {
                array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[1]</arg$argnmr>");
                $argnmr++;
                if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[2]))
                {
                    array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[2]</arg$argnmr>");
                    $argnmr++;
                    if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[3]))
                    {
                        array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[3]</arg$argnmr>");
                    }
                    else
                    {
                        constant_check($keyword[3], $argnmr, $xmlcode);
                    }
                }
                else
                {
                    constant_check($keyword[2], $argnmr, $xmlcode);
                    $argnmr++;
                    if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[3]))
                    {
                        array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[3]</arg$argnmr>");
                    }
                    else
                    {
                        constant_check($keyword[3], $argnmr, $xmlcode);
                    }
                }
            }
            else
            {
                exit(23);
            }
            array_push($xmlcode, "\t</instruction>");
            break;
        //no par
        case "POPFRAME":
        case "PUSHFRAME":
        case "CREATEFRAME":
        case "DEFVAR":
        case "RETURN":
        case "BREAK":
            if(count($keyword) !== 1)
            {
                exit(23);
            }
            array_push($xmlcode, "\t<instruction order=\"$loc\" opcode=\"".strtoupper($keyword[0])."\">\n\t</instruction>");
            break;
        //<symb>    
        case "DPRINT":
        case "EXIT":
        case "WRITE":
        case "PUSHS":
            if(count($keyword) !== 2)
            {
                exit(23);
            }
            array_push($xmlcode, "\t<instruction order=\"$loc\" opcode=\"$keyword[0]\">");
            $argnmr++;
            if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[1]))
            {
                array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[1]</arg$argnmr>");
            }
            else
            {
                constant_check($keyword[1], $argnmr, $xmlcode);
            }
            array_push($xmlcode, "\t</instruction>");
            break;
        //<label><symb1><symb2>
        case "JUMPIFEQ":
        case "JUMPIFNEQ":  
            if(count($keyword) !== 4)
            {
                exit(23);
            }
            if(array_search($keyword[1], $labelarray) !== false)
            {
                $pos = array_search($keyword[1], $labelarray);
                if($pos < $loc)
                {
                    $backjumps++;
                }
                else
                {
                    array_push($jumparray, $keyword[1]);
                }
                $jumps++;
            }
            else
            {
                array_push($jumparray, $keyword[1]);
            }
            $jumps++;
            array_push($xmlcode, "\t<instruction order=\"$loc\" opcode=\"$keyword[0]\">");
            $argnmr++;
            if(preg_match('/[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[1]))
            {
                array_push($xmlcode, "\t\t<arg$argnmr type=\"label\">$keyword[1]</arg$argnmr>");
                $argnmr++;
                if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[2]))
                {
                    array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[2]</arg$argnmr>");
                    $argnmr++;
                    if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[3]))
                    {
                        array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[3]</arg$argnmr>");
                    }
                    else
                    {
                        constant_check($keyword[3], $argnmr, $xmlcode);
                    }
                }
                else
                {
                    constant_check($keyword[2], $argnmr, $xmlcode);
                    $argnmr++;
                    if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[3]))
                    {
                        array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[3]</arg$argnmr>");
                    }
                    else
                    {
                        constant_check($keyword[3], $argnmr, $xmlcode);
                    }
                }
            }
            else
            {
                exit(23);
            }
            array_push($xmlcode, "\t</instruction>");
            break; 
        case "READ":
            if(count($keyword) !== 3)
            {
                exit(23);
            }
            array_push($xmlcode, "\t<instruction order=\"$loc\" opcode=\"$keyword[0]\">");
            $argnmr++;
            if(preg_match('/\b(LF|GF|TF)\b@[-a-zA-Z_$&%*!?][-a-zA-Z_$&%*!?0-9]*/', $keyword[1]))
            {
                array_push($xmlcode, "\t\t<arg$argnmr type=\"var\">$keyword[1]</arg$argnmr>");
                $argnmr++;
                if($keyword[2] == "bool" || $keyword[2] == "int" || $keyword[2] == "string" || $keyword[2] == "nil")
                {
                    array_push($xmlcode, "\t\t<arg$argnmr type=\"type\">$keyword[2]</arg$argnmr>\n\t</instruction>");
                }
                else
                {
                    exit(23);
                }
            }
            else
            {
                exit(23);
            }
            break;
        case "":
            break;
        default: 
            exit(22);
    }
}
// Pokud neobsahuje header, jedná se o chybu
if($header == false) 
{
    exit(21);
}
// Rozdělení fwjumps a badjumps
for($i = 0; $i < sizeof($jumparray); $i++)
{
    if(sizeof($jumparray) != 0){
        if(in_array($jumparray[$i], $labelarray))
        {
            $fwjumps++;
        }
        else
        {
            $badjumps++;
        }
}
}
// Vypíše všechny parametry pro sběr statistik
for($i = 2; $i < sizeof($argv); $i++)
{
    switch($argv[$i])
    {
        case "--comments":
            fwrite($file, "$comments\n");
            break;
        case  "--labels":
            fwrite($file, "$labels\n");
            break;
        case "--jumps":
            fwrite($file, "$jumps\n");
            break;
        case "--fwjumps":
            fwrite($file, "$fwjumps\n");
            break;
        case "--backjumps":
            fwrite($file, "$backjumps\n");
            break;
        case "--badjumps":
            fwrite($file, "$badjumps\n");
            break;
        default:
            if(substr($argv[$i], 0, 8) == "--stats=")
            {
                if(array_search($argv[$i], $statcall) !== false)
                {
                    exit(12);
                }
                else
                {
                    array_push($statcall, $argv[$i]);
                    $filename = explode('=', $argv[$i]);
                    $file = fopen($filename[1], 'w');
                    break;
                }
            }
            exit(10);
    }
}
// Vypsání XML reprezentace kodu
array_push($xmlcode, "</program>\n");
echo(implode("\n", $xmlcode));
exit(0);


// Funkce která kontroluje zda se jedná o konstantu
function constant_check($string, $argnmr, &$xmlcode)
{
    $check = explode('@', $string, 2);
    if(count($check) !== 2)
    {
        exit(23);
    }
    switch($check[0])
    {
        case "bool":
            if($check[1] != "false" | $check[1] != "true")
            {
                break;
            }else{
                exit(23);
            }
        case "string":
            $check[1] = preg_replace('/[&]/', '&amp;', $check[1]);
            $check[1] = preg_replace('/[<]/', "&lt;", $check[1]);
            $check[1] = preg_replace('/[>]/', '&gt;', $check[1]);
            if(preg_match_all('/[\\\\]/', $check[1]))
            {
                $err = preg_match_all('/[\\\\][0-9]{3}/', $check[1]);
                if($err == substr_count($check[1], "\\"))
                {
                    break;
                }
                else
                {
                    exit(23);
                }
            }
            break;
        case "int":
            if (preg_match('/^[+-]?[\d]+$/', $check[1])) 
            {
                break;
            } else {
                exit(23);
            }
        case "float":
                if(is_float($check[1]))
                {
                    break;
                } else {
                    exit(23);
                }
        case "nil":
            if($check[1] !== "nil")
            {
                exit(23);
            }
            break;
        default:
            exit(23);
    }
    array_push($xmlcode, "\t\t<arg$argnmr type=\"$check[0]\">$check[1]</arg$argnmr>");  
}