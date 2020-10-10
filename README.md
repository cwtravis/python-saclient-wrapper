# python-saclientutil
This project is a Python wrapper around the HCL AppScan on Cloud SAClient utility.
The SAClient.py script will aid in automation workflows where HCL does not have out-of-the box plug-ins or integrations.

# Prerequisites: 
  1. Have an HCL AppScan on Cloud account with API Key
  2. Install the SAClientUtil and add /bin to the path (tested with SAClient Version 8.0.1387)
  3. Install Python 3 (tested on 3.9.0)
  4. Have an application to scan
 
# Getting Started:

Start with the example script SAST_Automation_Example.py. This script will step through a simple static analysis automation workflow. An example credentials file is available in the example directory.
  1. Login to the ASoC service.
  2. Verify that the provided AppId exists in your ASoC subscription.
  3. Generate an IRX file using the provided appscan-config.xml file.
  4. Submit the IRX file for analysis, using the provided scan name.
  5. Monitor the scan progress and wait for it to complete.
  6. Download the scan summary as a json file and print some info about the scan.
  7. Download the scan report to a desired location.

By default, the example will not upload the irx file generated in step 1. It will upload the sample IRX file included in the example directory (demo.irx)
This file will scan very quickly for demo purposes. In a real use case, delete or comment out the line that uses demo.irx instead of the real IRX file.

The war file, included in the example directory is the Altoro Mutual (altoromutual.war). This is an application specifically designed to be scanned using HCL AppScan. It is publicly available at:  
<https://github.com/hclproducts/AltoroJ>


# Run the Example:  
Print the help and usage information
```
python SAST_Automation_Example.py -h 
usage: SAST_Automation_Example.py [-h] [-c CONFIG] [-s SCAN] [-t TARGET] credentials_file app

positional arguments:
  credentials_file      Path to file that contains ASoC API Key.
  app                   ID or Name of the application in ASoC to associate the scan with.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to AppScan Config XML File. If the config file resides in the target scan directory, this
                        option is not required.
  -s SCAN, --scan SCAN  Scan Name for the ASoC Portal. If not specified, a generic name is used.
  -t TARGET, --target TARGET
                        Directory to target for the scan. If not specified, the working directory is used.

File format for credentials file: {"keyid": "<KEYID>", "keysecret": "<KEYSECRET">}
```

Run the example workflow  
`py SAST_Automation_Example.py creds.json -c example/appscan-config.xml -s SAST_Scan -t example`

# Helpful Links:  
[HCL AppScan on Cloud Help Center](https://help.hcltechsw.com/appscan/ASoC/Welcome.html)  
	
# License

All files found in this project are licensed under the [Apache License 2.0](LICENSE).