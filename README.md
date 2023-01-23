
### Forward Networks Azure Update

When working with a large Azure environment, customers often add and remove subscriptions on a regular basis.  The collection via Forward Networks does not account for these regular changes, as we require an interactive powershell script to be run to create the appropriate credentials and generate the file needed for the app.

Requirements:

User must be logged into Azure and have access to Azure Powershell CmdLets

Script will create an App registration with the Service Principal name below.  If the Service Principal name exists, it will use this to assign the correct scopes

User must have credentials to post API to Forward Enterprise (or API key)

Required variables must be set prior to script execution

| Env Variable       | Required| Default                   | Note                           |
| ------------------ |---------|---------------------------| ------------------------------ |
| $Env:FWD_HOST      | Y       | N/A                       | Forward App Server             |
| $Env:FWD_NETWORKID | Y       | N/A                       | Network ID                     |
| $Env:FWD_USER      | Y       | N/A                       | Forward Username or API token  |
| $Env:FWD_PASSWORD  | Y       | N/A                       | Forward Password or API secret |
| $Env:SetupID       | N       | "azure_collect"           | Named Identifier for Sources   |
| $Env:SP_NAME       | N       | "ForwardServicePrincipal" | Azure Service Principal        |



Discalimer:

This software is provided as is, without any warranty or support. Use of the software is at your own risk. The author and any contributors will not be held responsible for any damages or issues that may arise from the use of this software.

Please be aware that this software may contain bugs, errors, or other issues. It may not function as intended or be fit for your specific use case.

By using this software, you acknowledge and accept the above disclaimer and assume all responsibility for any issues that may arise from its use.
