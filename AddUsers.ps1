# Configurations
$Domain = "ABC.INC"
$OU = "CN=Users,DC=ABC,DC=INC"  # Adjusted path for built-in Users container
$LogFile = "ADUserCreationLog.txt"

# Inline user configuration (Fallback)
$InlineUsers = @(
    @{Username="user51"; FirstName="Johnny"; LastName="Doe"; Password=""; EmailAddress="user51@abc.inc"; ipPhone="1051"},
    @{Username="user52"; FirstName="Alison"; LastName="Smith"; Password=""; EmailAddress="user52@abc.inc"; ipPhone="1052"}
    # Add more users here as needed
)

# Function to add a user
function Add-User {
    param (
        [string]$Username,
        [string]$FirstName,
        [string]$LastName,
        [string]$Password,
        [string]$EmailAddress,
        [string]$ipPhone
    )

    Write-Host "Processing user: $Username"
    if (Get-ADUser -Filter { SamAccountName -eq $Username } -ErrorAction SilentlyContinue) {
        Write-Host "User $Username already exists. Skipping..." -ForegroundColor Yellow
        "$($Username): Already Exists" | Out-File -Append $LogFile
    } else {
        try {
            New-ADUser -SamAccountName $Username `
                -UserPrincipalName "$Username@$Domain" `
                -Name "$FirstName $LastName" `
                -GivenName $FirstName `
                -Surname $LastName `
                -EmailAddress $EmailAddress `
                -OtherAttributes @{'ipPhone'=$ipPhone; 'telephoneNumber'=$ipPhone} `
                -AccountPassword (ConvertTo-SecureString $Password -AsPlainText -Force) `
                -Enabled $true `
                -Path $OU
            Write-Host "User $Username created successfully." -ForegroundColor Green
            "$($Username): Created Successfully" | Out-File -Append $LogFile
        } catch {
            Write-Host "Failed to create user $Username. Error: $_" -ForegroundColor Red
            "$($Username): Failed to Create - $_" | Out-File -Append $LogFile
        }
    }
}

# Main logic
if (Test-Path ".\users.csv") {
    Write-Host "Using CSV file as input."
    $Users = Import-Csv .\users.csv
} else {
    Write-Host "Using inline user configuration."
    $Users = $InlineUsers
}

# Ensure log file is clean
if (Test-Path $LogFile) { Remove-Item $LogFile }

# Process each user
foreach ($User in $Users) {
    Add-User -Username $User.Username -FirstName $User.FirstName -LastName $User.LastName `
        -Password $User.Password -EmailAddress $User.EmailAddress -ipPhone $User.ipPhone
}

Write-Host "Processing completed. Check $LogFile for details."
