<?php 

# definition of constants 
define("ERR_HEADER",21);
define("ERR_OPERATOR_CODE",22);
define("ERR_LEX_SYX", 23);
define("ERR_WRONG_PARAMS",10);
define("ERR_OPEN_INPUT_FILE", 11);
define("ERR_OPEN_OUTPUT_FILE",12);
define("ERR_INTERN", 99);
define("OK",0);

#default settings 
$dir="./";  ## directory in which I'm in 
$recursive = false; 
$parse_script = "./parse.php"; # input program parse.php
$int_script = "./interpret.py"; # input program interpret.py 
$parse_only = true; 
$int_only = true;
$xam = "jexamxml.jar" ;
### counting tests ###
$total_test =0;
$total_error=0;
$total_passed=0;
$test_result = array();
$tests = array();
?>