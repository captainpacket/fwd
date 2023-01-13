$apphost = 'fwd.app' 
$networkid = '154149'
$setupid = 'azure_collect'
$sp_name = 'ForwardServicePrincipal'

## Ensure Az.Resources is up to date

$resourceVersion = (Get-Module Az.Resources).version
$numberVersion = $resourceVersion.major * 100 + $resourceVersion.minor * 10 + $resourceVersion.build
if ($numberVersion -lt 531) {
    Write-host ("ERROR: The PowerShell module Az.Resources must be at least version 5.3.1")
    Write-host ("Update the module using the command: Update-Module -Name Az.Resources -Force")
    Write-host ("If the update fails because the package source cannot be found, register Azure's staging gallery and try updating again:`
                Register-PackageSource -ProviderName 'PowerShellGet' -Name 'PoshTestGallery' -Location https://www.poshtestgallery.com/api/v2")
    Write-host ("After module is updated, click on 'Restart Cloud Shell' to make sure latest version is loaded and then rerun this script")
    exit
}

## Check current user permissions or authenticate with another credentials

$uname = az ad signed-in-user show --query userPrincipalName -o tsv
$roles = Get-AzRoleAssignment -SignInName $uname

if (-not ($roles.RoleDefinitionName.Contains("Contributor") -or $roles.RoleDefinitionName.Contains("Owner"))) {
    Write-host ("Current user " + $uname + " does not have role Owner of Contributor assigned.")
    Write-host ("Do you want to login with another credentials?")
    $cont = Read-Host("Please type 'y' to authenticate with new credentials, anything else to exit")
    if ($cont.ToLower().Equals("y")) {
        Connect-AzAccount -UseDeviceAuthentication
    }
    else {
        Write-host ("Exiting")
        exit
    }
}
Write-host ("Current user " + $uname + " has enough permissions.")

## Select subscriptions

$subscriptions = Get-AzSubscription

## Show available subscriptions

Write-host ("Available subscriptions: ")

$i = 0
foreach ($s in $subscriptions) {
    Write-host("{0,5}" -f $i + " " + $s + "  " + $s.name)
    $i++
}

Write-host ("Please select subscriptions in which service principals will be created")
Write-host ("To select range, use ..                            : 4..6")
Write-host ("To select one item, use the index                  : 1")
Write-host ("To select list of items, use comma between indexes : 1,3")
Write-host ("To combine list and ranges use + sign              : 0,2+4..6")
Write-host ("Examples: '1' '1+3..5' '1,3,7' '1,3,7+9..12' '1,3,7+9..12+22..44' ")

$indexReadError = $true

while ($indexReadError) {

    $indexes = 0..10000
    $regex = '^(\d+(,\d+)*)(\+\d+\.\.\d+)*$|^(\d+\.\.\d+)(\+\d+\.\.\d+)*$'
    if ($indexes -notmatch $regex) {
        Write-Host "Wrong index format, please input correct indexes"
        Write-Host "Examples: '1' '1,3,7' '1,3,7+9..12' '1,3,7+9..12+22..44' "
        continue
    }
    try {
        $selectedSubscriptions = @()
        $uniqueIndexes = $indexes | Invoke-Expression | Sort-Object -unique
        $selectedSubscriptions += $subscriptions[$uniqueIndexes]
        Write-host ("Selected subscriptions are:")
        $selectedSubscriptions | Format-Table
        $indexReadError = $false
    }
    catch {
        Write-Output "Something went wrong, please input correct indexes"
    }
}


$scopes = @()
foreach ($s in $selectedSubscriptions) {
    $scopes += "/subscriptions/$s"
}


## Create service principal with Contributor role and assign all seclected subscriptions scope
Write-host ("Creating or updating service principal") 
$sp = Get-AzADServicePrincipal
if ($sp.DisplayName.Contains($sp_name)) {
   $sp = Get-AzADServicePrincipal -DisplayName $sp_name   
   $cl_s_p = New-AzADSpCredential -ServicePrincipalObject $sp
   }
else {
   $sp = New-AzADServicePrincipal -DisplayName $sp_name
   $cl_s_p = New-AzADSpCredential -ServicePrincipalObject $sp
   }

   
## define Subscription and Data_sources classes

class Subscription {
    [string]$subscriptionId
    [string]$clientId
    [string]$tenant
    [string]$secret
    [string]$environment
    [long]$testInstant
    [bool]$enabled

    Subscription(
        [string]$s_id,
        [string]$c_id,
        [string]$tnt,
        [string]$p,
	[string]$env,
	[long]$test,
	[bool]$enable
    ) {
        $this.subscriptionId = $s_id
        $this.clientId = $c_id
        $this.tenant = $tnt
        $this.secret = $p
	$this.environment = $env
	$this.testInstant = $test
	$this.enabled = $enable
    }
}

class Data_sources {
    [Subscription[]]$subscriptions
}

$user = (Get-Content .\creds.txt -TotalCount 2)[-2]
$pass = (Get-Content .\creds.txt -TotalCount 2)[-1]
$pair = "$($user):$($pass)"
$encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))
$basicAuthValue = "Basic $encodedCreds"
$Headers = @{
    Authorization = $basicAuthValue
}

$proxyurl = "https://" + $apphost + "/api/networks/" + $networkid + "/proxy"
$proxy = Invoke-WebRequest -Uri $proxyurl -Headers $Headers

$proxyps = ConvertFrom-Json $proxy

$data_sources = [Data_sources]::new()

$data_sources | Add-Member -Type NoteProperty -Name 'type' -Value 'AZURE'
$data_sources | Add-Member -Type NoteProperty -Name 'collect' -Value $true
$data_sources | Add-Member -Type NoteProperty -Name 'name' -Value $setupid 
$data_sources | Add-Member -Type NoteProperty -Name 'proxyServerId' -Value $proxyps.id 

foreach ($s in $selectedSubscriptions) {
    $scope = "/subscriptions/$s"
    Set-AzContext -SubscriptionObject $s
    New-AzRoleAssignment -ObjectId $sp.id -RoleDefinitionName Contributor -scope $scope 
    $cl_s_s_id = $s.id
    $cl_s_c_id = $sp.AppId
    $cl_s_t_id = $s.TenantId
    ##  $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sp.Secret)
    ##  $cl_s_p = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    $enabled = $true
    $test = Get-Date -UFormat %s 
    $subscription = [Subscription]::new($cl_s_s_id, $cl_s_c_id, $cl_s_t_id, $cl_s_p.SecretText, 'AZURE', $test, $true)
    $data_sources.subscriptions += $subscription
}

$json = "azure_subscriptions_" + [DateTime]::Now.ToString("yyyyMMdd-HHmmss") + ".json"
Write-host ("Saving to azure_subscriptions.json")
$data_sources | ConvertTo-Json | Out-File $json
Write-host ("Contents of azure_subscriptions.json")
$data_sources | ConvertTo-Json
Write-host ("Posting to " + $apphost)

$url = "https://" + $apphost + "/api/networks/" + $networkid + "/cloudAccounts"
$fullurl = "https://" + $apphost + "/api/networks/" + $networkid + "/cloudAccounts/" + $setupid  

$delete = Invoke-WebRequest -Method DELETE -Uri $fullurl -ContentType "application/json" -Headers $Headers
Write-Host ("Deleting old cloud setup: " + $delete.StatusCode + " " + $delete.StatusDescription)
Start-Sleep -Seconds 5
$update = Invoke-WebRequest -Method POST -Uri $url -Body ($data_sources|ConvertTo-Json) -ContentType "application/json" -Headers $Headers
Write-Host ("Writing new cloud setup: " + $update.StatusCode + " " + $update.StatusDescription)
