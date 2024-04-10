Write-Host "Get Option Data to excel"

$currentDirectory = Get-Location
Set-Location -Path $currentDirectory

# check if python is installed
# Split the PATH environment variable and search for python executable
$pythonExe = $env:PATH -split ";" | Where-Object { Test-Path $_\python.exe } | Select-Object -First 1

if ($pythonExe) {
    Write-Host "Python executable found: $pythonExe"
}
else {
    Write-Host "Python executable not found in PATH."
}

# Define the Django management command to run
$djangoCommand = "runserver"

# Define the host and port for the Django server
$hostname = "127.0.0.1"
$port = "8000"
$url = "${hostname}:$port"
Write-Host $url

# get inside directory one level
# cd pollpoc
Set-Location pollpoc

$djangoProcess = Start-Process -FilePath "python" -ArgumentList "manage.py $djangoCommand $url" -PassThru


# Wait for the Django server to start
Start-Sleep -Milliseconds 500  # Adjust the delay as needed

# Define the host URL based on the Django server settings
$hostUrl = "http://${hostname}:$port"
Write-Host host URL $hostUrl
Write-Host Django ProcessId $djangoProcess.Id

# Open the host URL in the default web browser
Start-Process $hostUrl

$processExist = Get-Process -Id $djangoProcess.Id

while ($true) {
    # Wait for a short interval before checking again
    Start-Sleep -Milliseconds 2000
    
    # Check if the browser tab is still open
    $tabOpen = Get-Process | Where-Object { $_.MainWindowTitle -like "*127.0.0.1*" }

    Write-Output $tabOpen
    Write-Output $tabOpen.Id
    if (-not $tabOpen) {
        Write-Output "Tab is closed"
        break
        
    }
    else {
        Write-Output "Tab is open"
    }
}

if ($processExist) {
    Stop-Process -Id $djangoProcess.Id
    Write-Output "Closed and Process stopped successfully." $processExist.Id
}

$newerPythonPIds = Get-Process | Where-Object { $_.ProcessName -eq "python" } | Select-Object -ExpandProperty Id

$newlyAddedPythonPIds = $newerPythonPIds | Where-Object { $_ -notin $olderPythonPIds }
Write-Host $newlyAddedPythonPIds

# Loop over the elements in $diffArray and stop the corresponding processes
foreach ($pidToStop in $newlyAddedPythonPIds) {
    Write-Host to stop $pidToStop
    Stop-Process -Id $pidToStop -Force
}

$afterPythonPIds = Get-Process | Where-Object { $_.ProcessName -eq "python" } | Select-Object -ExpandProperty Id
Write-Host $afterPythonPIds


# get one-level up in directory
# cd ..
Set-Location ..

# Pause to keep the PowerShell window open
Pause