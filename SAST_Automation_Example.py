# Example script to demonstrate static scan automation with
# HCL AppScan on Cloud and saclient.py
# Prerequisites: 
#    1. Have an HCL ASoC account with API Key
#    2. Install the SAClientUtil and add /bin to the path (tested with SAClient Version 6.0.1222)
#    3. Install Python 3, (This was developed and tested on 3.9.0)
#    4. Have an application to scan
#   5. (Optional) A well configured appscan-config.xml file
# Author: Cody Travis
# Email: cody.travis@hcl.com
# Date: 2020-10-06

import SAClient
import sys
import datetime
import argparse
import os
import json

def readCredsFile(filePath):
    try:
        file = open(filePath, "r")
        contents = file.read()
        credDict = json.loads(contents)
        file.close()
    except:
        return none
    return credDict

epilog = "File format for credentials file: {\"keyid\": \"<KEYID>\", \"keysecret\": \"<KEYSECRET\">}"
parser = argparse.ArgumentParser(epilog=epilog)
parser.add_argument("credentials_file", help="Path to file that contains ASoC API Key.")
parser.add_argument("app", help="ID or Name of the application in ASoC to associate the scan with.")
parser.add_argument("-c", "--config", help="Path to AppScan Config XML File. If the config file resides in the target scan directory, this option is not required.")
parser.add_argument("-s", "--scan", help="Scan Name for the ASoC Portal. If not specified, a generic name is used.")
parser.add_argument("-t", "--target", help="Directory to target for the scan. If not specified, the working directory is used.")

args = parser.parse_args()

api_key = None

print("=== Setup ===")
print("Processing Args")

#Check if credential file exists
if(args.credentials_file is not None and os.path.exists(args.credentials_file)==False):
    print("Credentials file doesn't exist. The file format should look like this:")
    print("{\"keyid\": \"<KEYID>\", \"keysecret\": \"<KEYSECRET>\"}")
    sys.exit(1)
else:
    #Check if credential file is in correct format.
    api_key = readCredsFile(args.credentials_file)
    if api_key:
        if "keyid" not in api_key.keys() or "keysecret" not in api_key.keys():
            print("Credential file is badly formatted. Look at the example in github or create on in this format:")
            print("{\"keyid\": \"<KEYID>\", \"keysecret\": \"<KEYSECRET>\"}")
        else:
            print("API Key successfully loaded from credentials file.")
    else:
        print("Error readying the credentials file")
        sys.exit(1)
    
if(args.config is not None and os.path.exists(args.config)==False):
    print("Config file does not exist")
    sys.exit(1)
else:
    configFile = args.config

if args.target is not None and os.path.exists(args.target)==False and os.path.isdir(args.target)==False:
    print("Target directory {"+str(args.target)+"} not found.")
    print("Exiting")
    sys.exit(1)
else:
    targetDir = args.target
    os.chdir(targetDir)
    print("Changed working directory to target directory:\n"+str(os.getcwd()))
    
if(args.scan is not None):
    scanName = args.scan
else:
    scanName = "Static_Scan"

print()

appidentifier = args.app
debug = True
saclient = SAClient.SAClient(api_key["keyid"], api_key["keysecret"], False, debug)

# Step 1: Login to ASoC
print("=== Step 1: Login to ASoC ===")
if not saclient.loginASoC():
    print("Could not login to ASoC... bad API key?")
    print("Exiting")
    sys.exit(1)

print("Logged in successfully")
app = saclient.findSingleApp(appidentifier)
print()

print("=== Step 2: Verify the App Exists ===")
if not app:
    print("Could not find app: "+str(appidentifier))
    print("Check ASoC portal and verify app name or id is correct")
    print("Exiting")
    sys.exit(1)
    
print("Application Found: Name ["+str(app["name"])+"] Id ["+str(app["id"])+"]")
print()

# Step 3: Generate IRX File
print("=== Step 3: Generate the IRX File ===")
irxFile = saclient.generateIRX(scanName, configFile)
if(irxFile is None):
    print("Something went wrong generating IRX File")
    sys.exit(1)
scanName = irxFile
irxFile = irxFile + ".irx"
print("IRX File Generated: " + irxFile)
print()

# Step 4: Submit IRX File for Analysis
print("=== Step 4: Submit IRX File to ASoC for Analysis ===")
scanId = saclient.queueAnalysis(irxFile, scanName, app["id"])
if(scanId is None):
    print("Something went wrong while submitting the IRX File")
    sys.exit(1)
else:
    print("Scan Created: " + scanId)
print()

# Step 5: Wait for the scan to complete
print("=== Step 5: Wait for the scan to complete ===")
result = "Failed"
result = saclient.waitForScan(scanId, printStatusEveryMins=1)
 
if(result != "Ready"):
    print("Problem waiting for scan to finish: Reason - " + result)
    saclient.destroyToken()
    sys.exit(1)
print("Scan is Complete (status='Ready')")
print()

# Step 6: Retrieve Scan Results
print("=== Step 6: Retrieve Scan Results and Save to File ===")
summary = saclient.getScanSummary(scanId, scanName+"_result.json")
if(summary is None):
    print("Something went wrong getting the scan summary")
    saclient.destroyToken()
    sys.exit(1)
    
print("Scan Summary:")
print("  Status: " + summary["LatestExecution"]["Status"] + " (" + summary["LatestExecution"]["ExecutionProgress"] + ")")
startTime = datetime.datetime.strptime(summary["LatestExecution"]["CreatedAt"], '%Y-%m-%dT%H:%M:%S.%fZ')
endTime = datetime.datetime.strptime(summary["LatestExecution"]["ScanEndTime"], '%Y-%m-%dT%H:%M:%S.%fZ')
print("  Scan Duration: " + saclient.strfdelta(endTime-startTime, "{days}d {hours}h {minutes}m {seconds}s"))
print("  High Issues: " + str(summary["LatestExecution"]["NHighIssues"]))
print("  Medium Issues: " + str(summary["LatestExecution"]["NMediumIssues"]))
print("  Low Issues: " + str(summary["LatestExecution"]["NLowIssues"]))
print("  Info Issues: " + str(summary["LatestExecution"]["NInfoIssues"]))
print()
print("  Total Issues: " + str(summary["LatestExecution"]["NIssuesFound"]))
print("Saved Scan Summary JSON File: " + scanName+"_result.json")
print("Use this file for further automation.")
print()

# Step 7: Download HTML Report
print("=== Step 7: Download HTML Report ===")
result = saclient.getReport(scanId, scanName+"_report.html", "html")
if(result == False):
    print("Problem downloading report")
    saclient.destroyToken()
    sys.exit(1)

print("Report Downloaded and saved to " + scanName+"_report.html")
print()

print("=== Static Scan Automation Complete ===")

#Copyright 2018 Cody Travis

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#  http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.