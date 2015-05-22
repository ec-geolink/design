<?php
$url = 'http://www.bco-dmo.org/rdf/geolink';
$content = file_get_contents($url);
$json = json_decode($content, true);

foreach ($json as $idx => $data) {
  if (!empty($data['dcat:downloadURL']) && !empty($data['dct:title'])) {
    $file = getcwd() . '/' . $data['dct:title'];
    echo 'storing ' . $data['dcat:downloadURL'] . ' at ' . $file . "\n";
    file_put_contents($file, fopen($data['dcat:downloadURL'], 'r'));
  }
}
echo "done.";
?>
