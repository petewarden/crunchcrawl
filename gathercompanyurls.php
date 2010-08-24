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

    preg_match_all(
        '@<li><a href="([^"]+)" title="([^"]+)">([^<]+)</a></li>@',
        $content,
        $matches);
        
    $match_array = $matches[1];
    foreach ($match_array as $match_text)
        fwrite($output_handle, $match_text."\n");
}

$cliargs = array(
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

$output = $options['output'];
$max_requests = $options['maxrequests'];
$organization = $options['organization'];
$email = $options['email'];

$terms_list = range('a', 'z');
$terms_list[] = 'other';

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

$output_handle = fopen($output, 'w');

$parallel_curl = new ParallelCurl($max_requests, $curl_options);

foreach ($terms_list as $terms) {
    $page_url = 'http://www.crunchbase.com/companies?c='.urlencode($terms);
    $data = array('output_handle' => $output_handle);
    $parallel_curl->startRequest($page_url, 'on_request_done', $data);
}

// This should be called when you need to wait for the requests to finish.
// This will automatically run on destruct of the ParallelCurl object, so the next line is optional.
$parallel_curl->finishAllRequests();

?>