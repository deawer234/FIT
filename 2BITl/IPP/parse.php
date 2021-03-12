<?php
ini_set('display_errors', 'stderr');
$xmlcode = [];
array_push($xmlcode, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
$filename = [];
$file;
$argvs = [];
$statcall = []; 

if($argc > 1)
{
    if($argv[1] == "--help")
    {
        echo("help placeholder");
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
            //array_push($labelarray, $keyword);
            if(!empty($keyword[1]))
                $labelarray[$loc] = $keyword[1];
            $labels++;
            //$lastlabel = $loc;
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
        //no arg
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
                $jumparray[$loc] = $keyword[1];
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
if($header == false) 
{
    exit(21);
}
for($i = 0; $i < sizeof($jumparray); $i++)
{
    if(in_array($jumparray[$i], $labelarray))
    {
        $fwjumps++;
    }
    else
    {
        $badjumps++;
    }
}

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
array_push($xmlcode, "</program>\n");
echo(implode("\n", $xmlcode));
exit(0);

function constant_check($string, $argnmr, &$xmlcode)
{
    $check = explode('@', $string);
    switch($check[0])
    {
        case "bool":
            if($check[1] != "false" & $check[1] != "true")
            {
                exit(23);
            }
            break;
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
            /*if (preg_match('/^[0-9]+$/', $check[1])) 
            {
                echo("<arg$argnmr type=\"$check[0]\">$check[1]</arg$argnmr>");
            } else {
                exit(23);
            }
            $counter = 0;
            for($i = 0;$i < strlen($check[1]);$i++){
                if($check[1][$counter] == ' ')
                    $counter++;
            }
            $check[1] = substr($check[1], $counter, strlen($check[1]));*/
            if($check[1] == "")
            {
                exit(23);
            }
            break;
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