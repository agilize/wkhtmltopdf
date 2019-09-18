wkhtmltopdf Microservice
========================

Alpine container service for [wkhtmltopdf](https://wkhtmltopdf.org/).

## Requirements

* Work only with zip files
* Should have a index.html

## Usage

Run Container
```bash
docker run -d -p 29881:80 agilize/wkhtmltopdf
(cd ./demo && zip -r ../demo.zip .)
curl -X POST -vv -F 'file=@demo.zip' http://localhost:29881 -o demo.pdf
```

### PHP example

```php
<?php

/**
 * $directory_path string
 * $output string
 */
function zip_directory($rootPath, $output) {
    // Initialize archive object
    $zip = new \ZipArchive();
    $zip->open($output, \ZipArchive::CREATE | \ZipArchive::OVERWRITE);

    // Create recursive directory iterator
    /** @var SplFileInfo[] $files */
    $files = new \RecursiveIteratorIterator(
        new \RecursiveDirectoryIterator($rootPath),
        \RecursiveIteratorIterator::LEAVES_ONLY
    );

    foreach ($files as $name => $file)
    {
        // Skip directories (they would be added automatically)
        if (!$file->isDir())
        {
            // Get real and relative path for current file
            $filePath = $file->getRealPath();
            $relativePath = substr($filePath, strlen($rootPath) + 1);

            // Add current file to archive
            $zip->addFile($filePath, $relativePath);
        }
    }

    // Zip archive will be created only after closing object
    $zip->close();
}

$demoPath = realpath('./demo');
$zipFilePath = tempnam('/tmp', 'demo') . '.zip';

zip_directory($demoPath, $zipFilePath);

$wkhtmltopdfOptions = [
    'page-size' => 'Letter',
    'T' => '0', // remove margins using: ["B" => "0", "L" => "0", "R" => "0", "T" => "0"]
];

// set request body
$data = [
    'file' => curl_file_create($zipFilePath),
    'options' => json_encode($wkhtmltopdfOptions)
];

// set header
$headers = [
];

// curl options
$options = [
    CURLOPT_URL            => 'http://localhost/',
    CURLOPT_PORT           => 29881,
    CURLOPT_POST           => 1,
    CURLOPT_POSTFIELDS     => $data,
    CURLOPT_HTTPHEADER     => $headers,
    CURLOPT_RETURNTRANSFER => true
];

// curl call
$ch = curl_init();
curl_setopt_array($ch, $options);
$result = curl_exec($ch);
curl_close($ch);

unlink($zipFilePath);

// print result
echo $result;
```