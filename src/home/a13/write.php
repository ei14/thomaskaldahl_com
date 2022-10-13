<?php
$numfile = fopen("num.txt", "w");
$num = $_GET["num"];
if(is_numeric($num)) {
	fwrite($numfile, $num);
}
fclose($numfile);
