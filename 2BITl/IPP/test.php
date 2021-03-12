<?php 

#
# Name: test.php
# Caption: Project 2 of IPP  
# Author: Magdaléna Ondrušková <xondru16@stud.fit.vutbr.cz>
# Date: 21.03.2020
#

#TODO rozšírenie 
#TODO prepísať test_out test_src na parse_out... 

require_once __DIR__.'/testlib/test_default_settings.php';
require_once __DIR__.'/testlib/test_arguments.php';
require_once __DIR__.'/testlib/test_control.php';



###### MAIN PROGRAM ######
checkArguments();
doTests();
## musí byť tu, inak to nefunguje   
require_once __DIR__.'/testlib/test_html.php';
?>