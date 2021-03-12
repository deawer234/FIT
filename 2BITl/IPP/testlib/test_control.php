<?php
#################################
# Function loads all test paths #
#    that contains src files    #
#  and returns it in @testPaths #
#################################
function loadTestPaths()
{
    global $recursive;
    global $dir; 

    ## argument recursive is present
    if ($recursive)
    {
        exec("find " . $dir . " -regex '.*\.src$'", $testPaths); 
    }
    ## looking for test files only in given dir
    else 
    {
        exec("find ". $dir . " -maxdepth 1 -regex '.*\.src$'", $testPaths);
    }
    return $testPaths;
}

#################################
#   Function loads and return   #
#           test path           # 
#################################
function loadPath($test)
{
    $test_name = preg_split('/\//', $test);
    $index = array_key_last($test_name);
    $test_path = $test_name[0] . "/";
    for ( $i = 1; $i < $index; $i++)
    {
        $test_path = $test_path . $test_name[$i] . "/"; 
    }
    return $test_path;
}

#################################
#        Function returns       #
#        test: test.src         #
#################################
function getTestFileSrc($test)
{
    $test_name = preg_split('/\//', $test);
    $index = array_key_last($test_name);
    $test_name = $test_name[$index];
    return $test_name;
}

#################################
#        Function returns       #
#        test: test.in          #
#################################
function getTestFileIn($test, $test_path)
{
    $test = $test_path. $test . ".in"; 
    # if the file doesn't exist 
    # it creates empty file
    if (!file_exists($test))
    {  
        $file_in=fopen($test,"w");
        if ($file_in === false )
        {
            exit (ERR_OPEN_OUTPUT_FILE);
        }
        fclose($file_in);
    }
    return $test;
}

#################################
#        Function returns       #
#        test: test.out         #
#################################
function getTestFileOut($test, $test_path)
{
    $test = $test_path . $test . ".out"; 
    # if the file doesn't exist 
    # it creates empty file
    if (!file_exists($test))
    {  
        $file_out=fopen($test,"w");
        if ($file_out === false )
        {
            exit (ERR_OPEN_OUTPUT_FILE);
        }
        fclose($file_out); 
    }
    return $test;
}

#################################
#        Function returns       #
#          review code          #
#################################
function getTestFileRC($test, $test_path)
{
    $test = $test_path.$test . ".rc"; 
    # if the file doesn't exist 
    # it creates file with 0 (program run without error) in it
    if (!file_exists($test))
    {  
        $file_rc=fopen($test,"w");
        if ( $file_rc === false )
        {
            exit (ERR_OPEN_OUTPUT_FILE);
        }
        fwrite($file_rc,"0");
        fclose($file_rc); 
        $rc = 0; 
    }
    else 
    { 
        $file_rc = fopen($test,"r");
        if ($file_rc === false )
        {
            exit (ERR_OPEN_OUTPUT_FILE);
        }
        $rc = intval(fread($file_rc, filesize($test))); ## reads value from file 
    }
    return $rc;
}

#################################
#   Function loads test-suites  # 
#          statistics           #
#################################
function loadTestsStatistic($first, $test_path, $index )
{
    global $test_result;
    if ($first )
    {
        $index++;
        $test_result[$index]["test_name"] = $test_path;
        $test_result[$index]["total_test"] = 1; 
        $test_result[$index]["passed"] = 0;
        $test_result[$index]["error"] =0;
    }
    else if ( $test_result[$index]["test_name"] === $test_path)
        # Prirítanie k počtu celkovo testov v danom testovacom súbore 
    {
        $test_result[$index]["total_test"] ++; 
    }
    else 
    {
        $index++;
        $test_result[$index]["test_name"] = $test_path;
        $test_result[$index]["total_test"] = 1; 
        $test_result[$index]["passed"] = 0;
        $test_result[$index]["error"] =0;
    }
    return $index; 
}

#################################
##   Function runs parse.php   ##
#################################
function testParsephp($test_path, $test_src, $test_name, $index, $test_rc,$test_out,$i)
{
    global $parse_script;
    global $total_passed;
    global $total_error;
    global $test_result;
    global $xam;
    global $tests;

    $test_yourrc = 0;  ## return code returned by running the script 
     ## $test_yourout  -  output returned by running the script       ##
    exec("php7.4 " . $parse_script  . " < " . $test_path . "$test_src", $test_yourout, $test_yourrc );
    $test_yourout= shell_exec("php7.4 " . $parse_script . " < " . $test_path . $test_src);  ## because exec doesn't return white spaces \n 
    ## writing output to file 
    $test_yourout_file = $test_path.$test_name[0] . ".yourout"; 
    $parse_file = fopen($test_yourout_file,"w"); 
    if ($parse_file === false )
    {
        exit (ERR_OPEN_OUTPUT_FILE);
    }
    fwrite($parse_file, $test_yourout); 
    fclose($parse_file); 

    # controls return code and output 
    exec("java -jar " . $xam . " " . $test_out . " ". $test_yourout_file . " diffs.xml /D /pub/courses/ipp/jexamxml/options", $tmp_out, $xaml_rc);
    if ($test_yourrc === OK && $test_yourrc === $test_rc && $xaml_rc === OK)
    {
        $total_passed++;
        $test_result[$index]["passed"]++;
        $passed = true; 
    }
        else if ( $test_rc === $test_yourrc && $test_rc !== OK)
        {

            $total_passed++;
            $test_result[$index]["passed"]++;
            $passed = true; 
        }
        else 
        {
            $total_error++;
            $test_result[$index]["error"]++;
            $passed = false; 
        }
        ##spravý názov test-suitu a hlavičku + prvý riadok tabuľky 
        $tests[$i]["path"] = $test_path; 
        $tests[$i]["name"] = $test_src;
        $tests[$i]["passed"] = $passed;
        $i++;
        # delete tmp file
        unlink($test_yourout_file); 
        return $i;
}

function testInterpretpy($test_path, $test_name, $test_src, $test_in, $test_out, $i,$test_rc, $index)
{
    global $int_script;
    $interpret_rc = 0; 
    global $total_passed; 
    global $total_error; 
    global $test_result;
    global $tests;
    $test_src = $test_path . $test_src; 
    exec("python3.8 " . $int_script  . " --source=". $test_src . " < " . $test_in, $interpret_yourout, $interpret_rc); 
    $interpret_yourout = shell_exec("python3.8 " . $int_script  . " --source=". $test_src . " < " . $test_in);
    $interpret_yourout_file = $test_path.$test_name[0].".intyourout"; 
    $interpret_file = fopen($interpret_yourout_file, "w");
    if ( $interpret_file === true )
    {
        exit (ERR_OPEN_OUTPUT_FILE);
    }
    fwrite($interpret_file,$interpret_yourout); 
    fclose($interpret_file);
    $diff_rc = 1;
    if ( $test_rc === OK)
    {
        exec("diff ". $test_out . " " . $interpret_yourout_file , $difference, $diff_rc);
    }
    if ($interpret_rc === OK &&  $test_rc  === $interpret_rc && $diff_rc === OK )
    {
        $total_passed++;
        $test_result[$index]["passed"]++;
        $passed = true;if ( $test_rc === OK);
        
    }
    else if ( $interpret_rc === $test_rc && $test_rc !== OK)
    {   
        $total_passed++;
        $test_result[$index]["passed"]++;
        $passed = true;if ( $test_rc === OK);
    }
    else
    {
        $total_error++;
        $test_result[$index]["error"]++;
        $passed = false;
    }
    $tests[$i]["path"] = $test_path; 
    $tests[$i]["name"] = $test_src;
    $tests[$i]["passed"] = $passed;
    $i++;

    #delete temporary file
    unlink($test_path.$test_name[0].".intyourout");
    return $i;
}

#################################
#  Function runs both parser    # 
#     and also interpret        #
#################################
function doBothTest($test_path, $test_name, $test_src, $test_in, $test_out,  $i,$test_rc, $index)
{
    global $parse_script;
    global $int_script;
    global $total_passed; 
    global $total_error; 
    global $test_result;
    global $tests;
    
    exec("php7.4 " . $parse_script  . " < " . $test_path . "$test_src", $test_yourout, $test_yourrc );
    ###parse script runned without error, so i start running interpret. 
    if ($test_yourrc === OK)
    {
        $test_yourout= shell_exec("php7.4 " . $parse_script . " < " . $test_path . $test_src);  ## because exec doesn't return white spaces \n 
        # write XML output as new src 
        $test_yoursrc_file = $test_path. $test_name[0]. ".yoursrc";
        $xml_file = fopen($test_yoursrc_file, "w");
        if ($xml_file === false)
        {
            exit(ERR_OPEN_OUTPUT_FILE);
        }
        fwrite($xml_file, $test_yourout);
        fclose($xml_file);
        # runs interpret.py
        exec("python3.8 " . $int_script  . " --source=". $test_yoursrc_file . " < " . $test_in, $interpret_yourout, $interpret_rc); 
        $interpret_yourout = shell_exec("python3.8 " . $int_script  . " --source=". $test_yoursrc_file . " < " . $test_in);
        $interpret_yourout_file = $test_path.$test_name[0].".yourout"; 
        $interpret_file = fopen($interpret_yourout_file, "w");
        if ( $interpret_file === true )
        {
            exit (ERR_OPEN_OUTPUT_FILE);
        }
        fwrite($interpret_file, $interpret_yourout); 
        fclose($interpret_file);
        $diff_rc = 1;
        if ( $test_rc === OK)
        {
            exec("diff ". $test_out . " " . $interpret_yourout_file , $difference, $diff_rc);
        }
        if ($interpret_rc === OK &&  $test_rc  === $interpret_rc && $diff_rc === OK )
        {
            $total_passed++;
            $test_result[$index]["passed"]++;
            $passed = true;if ( $test_rc === OK);
        
        }
        else if ( $interpret_rc === $test_rc && $test_rc !== OK)
        {   
            $total_passed++;
            $test_result[$index]["passed"]++;
            $passed = true;if ( $test_rc === OK);
        }
        else
        {
            $total_error++;
            $test_result[$index]["error"]++;
            $passed = false;
        }
    }
    else if ( $test_yourrc === $test_rc)
    {
        $total_passed++;
        $test_result[$index]["passed"]++;
        $passed = true; 
    }
    else 
    {
        $total_error++;
        $test_result[$index]["error"]++;
        $passed = false; 
    }

    $tests[$i]["path"] = $test_path; 
    $tests[$i]["name"] = $test_src;
    $tests[$i]["passed"] = $passed;
    $i++;

    #delete temporary file
    unlink($test_path.$test_name[0].".yourout");
    unlink($test_path.$test_name[0]. ".yoursrc");
    return $i;
}


#################################
#  Function runs all the tests  #
#################################
function doTests()
{
    global $total_test;
    global $parse_only;
    global $int_only;
    $first = true; 
    $index = -1; 
    $i =0;
    $testPaths = loadTestPaths();
    foreach ($testPaths as $test)
    {
       
        $total_test++;  
        $test_path = loadPath($test);         
        $index=loadTestsStatistic($first,$test_path,$index);
        $first = false;
       
        $test_src = getTestFileSrc($test);
        ##splits test name by dot 
        $test_name = preg_split('/\./', $test_src);
        ## gets the rest of testing files names
        $test_in = getTestFileIn($test_name[0],$test_path);
        
        $test_out = getTestFileOut($test_name[0], $test_path);
        $test_rc = getTestFileRC($test_name[0], $test_path); 
        if (  $int_only &&  $parse_only)
        {
            $i = doBothTest($test_path, $test_name, $test_src, $test_in, $test_out,  $i,$test_rc, $index);
        }
        else if ( $int_only && ! $parse_only )
        {
            $i = testInterpretpy($test_path, $test_name, $test_src, $test_in, $test_out, $i,$test_rc, $index);
        }
        else if ( $parse_only  && ! $int_only)
        {
            $i = testParsephp($test_path, $test_src, $test_name, $index, $test_rc,$test_out,$i);
        }
    }
}
?>