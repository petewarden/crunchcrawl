#!/usr/bin/php
<?php
// 
//
// By Pete Warden <pete@petewarden.com>, freely reusable, see http://petewarden.typepad.com for more

require_once('parallelcurl.php');
require_once('cliargs.php');

// This function gets called back for each request that completes
function on_request_done($content, $url, $ch, $data) {
    
    $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);    
    if ($httpcode !== 200) {
        print "Fetch error $httpcode for '$url'\n";
        return;
    }
    
    $output_handle = $data['output_handle'];

    $text = str_replace("\n", "", $content);

    fwrite($output_handle, $text."\n");
}

$cliargs = array(
	'input' => array(
		'short' => 'i',
		'type' => 'required',
		'description' => 'The file to read the list of company URLs from',
	),
	'output' => array(
		'short' => 'o',
		'type' => 'optional',
		'description' => 'The file to write the output list of URLs to - if unset will write to stdout',
        'default' => 'php://stdout',
	),
    'maxrequests' => array(
        'short' => 'm',
        'type' => 'optional',
        'description' => 'How many requests to run in parallel',
        'default' => '10',
    ),
    'organization' => array(
        'short' => 'r',
        'type' => 'required',
        'description' => 'The name of the organization or company running this crawler',
    ),
    'email' => array(
        'short' => 'e',
        'type' => 'required',
        'description' => 'An email address where server owners can report any problems with this crawler',
    ),    
);	

ini_set('memory_limit', '-1');

$options = cliargs_get_options($cliargs);

$input = $options['input'];
$output = $options['output'];
$max_requests = $options['maxrequests'];
$organization = $options['organization'];
$email = $options['email'];

if (empty($organization) || empty($email) || (!strpos($email, '@')))
    die("You need to specify a valid organization and email address (found '$organization', '$email')\n");

$agent = 'Crawler from '.$organization;
$agent .= ' - contact '.$email;
$agent .= ' to report any problems with my crawling. Based on code from http://petewarden.typepad.com';

$curl_options = array(
    CURLOPT_SSL_VERIFYPEER => FALSE,
    CURLOPT_SSL_VERIFYHOST => FALSE,
	CURLOPT_FOLLOWLOCATION => TRUE,
	CURLOPT_USERAGENT => $agent,
);

$urls_string = file_get_contents($input);
$urls = split("\n", $urls_string);

$output_handle = fopen($output, 'w');

$parallel_curl = new ParallelCurl($max_requests, $curl_options);

$count = 0;

foreach ($urls as $url) {

    $count += 1;
    if (($count%100)==0)
        error_log("Completed $count urls");

    if (!preg_match('@^/company/@', $url))
        continue;
        
    $full_url = 'http://api.crunchbase.com/v/1'.$url.'.js';
    $data = array('output_handle' => $output_handle);
    $parallel_curl->startRequest($full_url, 'on_request_done', $data);
}

// This should be called when you need to wait for the requests to finish.
// This will automatically run on destruct of the ParallelCurl object, so the next line is optional.
$parallel_curl->finishAllRequests();

?>