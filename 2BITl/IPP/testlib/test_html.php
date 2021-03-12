<?php 
   
###############################
## Function adds test-suites ##
##     statistic to html     ##
###############################
function add_test_suites()
    {
        global $test_result;
        foreach ($test_result as $test)
        {
?>            
            <tr>
                <td> <?php echo $test["test_name"] ?> </td>
                <td> <?php echo $test["total_test"] ?> </td>
                <td> <div class= passed > <?php echo $test["passed"] ?> </div></td>
                <td> <div class= not-passed > <?php echo $test["error"] ?> </div></td>
            </tr>

<?php
        }
    }
?>

<?php

#############################
##  Function adds test to  ##
##  the table with result  ##
#############################
function add_test()
{
    $first = true;
    global $tests;
    $dir = "";
    foreach ($tests as $test)
    {   
        if ( $dir !== $test["path"] && ! $first )
        {
            ?>
            </table>
            <hr>
            <?php
            $first = true; 
        }
        # treba nastaviť aj nadpis tabuľky a pridá prvý test do nej
        if ($first)
        {
?>
            <b>Test suite: </b> <?php echo $test["path"] ?>
            <table align="center">
            <tr>
            <th> Test name </th>
            <th> Result </th>
            </tr>
<?php 
        
            $first = false;
        }
?>
        <tr> 
                <td> <?php echo $test["name"] ?> </td>
<?php 
        #test passed 
            if ($test["passed"])
            {
?> 
            <td> <div class = passed> <?php echo "Passed" ?> </div></td>
<?php
            }
            #test didn't passed
            else
            {
?>
                <td> <div class = not-passed> <?php echo "Error" ?> </div></td>
<?php
            }
?>
        </tr>
        
<?php        
        $dir = $test["path"];
    }
}
?>


<!DOCTYPE HTML>
<html lang="en">
<head>
    <meta charset = "UTF-8">
    <title>
    IPP: Test results
    </title>

<style>
    body /*  pozadie  */
    {
        background-color: #ECFFEE;
        margin: 30px; 
        font-family: Arial, Helvetica, sans-serif;
        font-size: 15px;
    }
    hr /* oddeľujúca čiara */
    {
        display: block;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
        margin-left: auto;
        margin-right: auto;
        border-style: inset;
        border-width: 3px;
    }
    table th, td
    {
        border: 1.2px solid black; 
        padding-left: 10px;
        padding-right: 10px;
        padding-bottom: 7px;
        padding-top: 7px;
        font-size: 15px;
    }
    table th
    {
        background-color: #BFDFFF;
        text-align: center;
    }
    table tr:nth-child(even)
    {
        background-color: #E5F2FF;
    }
    table tr:nth-child(odd)
    {
        background-color: #D3E9FF
    }

    /* my classes */
    .header /* hlavička  */
    {
        font-size: 40px; 
        color: #083059; 
        text-align: center; 
    }
    .sum /* suma všetkých testov - prehľad */
    {
        font-size: 30px; 
        color: #083059; 
        text-align: left; 
    }
    .test_suite_header /* nadpis pre jednotlivé test-suites */
    {
        text-align: center;
        font-size: 30px;   
        color: #083059;
        padding-bottom: 10px;
    }
    .passed /*  pozadie pre testy, ktoré prešli */
    {
        color: #05B31A
    }
    .not-passed /* pozadie pre testy, ktoré neprešli */ 
    {
        color: #FF0000
    }
</style>
</head>

<body> 
<div class = header >
       <b> IPP 2020 project test results </b>
</div> 

<div class = sum>  
    Total tests: <b> <?php echo $total_test;?> </b> 
    <div class = passed>
        Total passed tests: <b> <?php echo $total_passed;?> </b> 
    </div>

    <div class = not-passed >
         Total error tests: <b> <?php  echo $total_error;?> </b>
    </div>
    <hr>
</div>

<div class= test_suite_header>
    <b> Test suites </b>
    <table align="center">
        
        <tr>
            <th> Test suite </th>
            <th> Total tests </th>
            <th> Total passed </th>
            <th> Total error </th>
        </tr>
        <tr>
            <?php add_test_suites($test_result); ?>
        </tr>
    </table>
<hr>
</div>


<div class= test_suite_header > 
    <?php add_test() ?>
</div>

</body>
</html>