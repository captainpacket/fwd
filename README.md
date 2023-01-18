When working with a large Azure environment, customers often add and remove subscriptions on a regular basis.  The collection via Forward Networks does not account for these regular changes, as we require an interactive powershell script to be run to create the appropriate credentials and generate the file needed for the app.

Requirements:

User must be logged into azure.  Script will prompt for Azure login interactively if not completed; otherwise script is non-interactive.

Script will create an App registration with the Service Principal name below.  If the Service Principal name exists, it will use this to assign the correct scopes

User must have credentials to post API to Forward Enterprise (or API key)

Variables (must be set prior to script execution):

$Env:AppHost = "fwd.app"                      #{Or other instance}

$Env:NetworkID = "123456"                     #{Replace with Forward Networks Network ID}

$Env:SetupID = "azure_collect"                #{Leave as default or change to preferred ID}

$Env:FwdUser = "XXXXXXX"                      #{Forward Networks username or API token}

$Env:FwdPass = "XXXXXXX"                      #{Forward Networks password}

$Env:ServicePrincipal = "ForwardSP"           #{Name of desired Azure Service Principal to use - will create if does not exit}


This software is provided as is, without any warranty or support. Use of the software is at your own risk. The author and any contributors will not be held responsible for any damages or issues that may arise from the use of this software.

Please be aware that this software may contain bugs, errors, or other issues. It may not function as intended or be fit for your specific use case.

By using this software, you acknowledge and accept the above disclaimer and assume all responsibility for any issues that may arise from its use.
