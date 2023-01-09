$PYTHON_ZIP = Join-Path $PSScriptRoot "python-3.10.9-embed-amd64.zip"
$GETPIP_PY = Join-Path $PSScriptRoot "get-pip.py"
$TARGET_ROOT = Join-Path (Split-Path $PSScriptRoot -Qualifier) AEGP
$PYTHON_ROOT = Join-Path $TARGET_ROOT "AEPython\\python-3.10.9-embed-amd64"
$PYTHON_EXE = Join-Path $PYTHON_ROOT "python.exe"
$PTH = Join-Path $PYTHON_ROOT "python310._pth"

if (!(Test-Path $PYTHON_ZIP)){
    Invoke-WebRequest "https://www.python.org/ftp/python/3.10.9/python-3.10.9-embed-amd64.zip" -OutFile $PYTHON_ZIP
}

if (!(Test-Path $GETPIP_PY)){
    Invoke-WebRequest "https://bootstrap.pypa.io/get-pip.py" -OutFile $GETPIP_PY
}

if (!(Test-Path $PYTHON_ROOT)){
    Expand-Archive -Path $PYTHON_ZIP -DestinationPath $PYTHON_ROOT
    cd $PYTHON_ROOT

    (Get-Content -Path $PTH) -replace "#import site", "import site" | Set-Content -Path $PTH
    .\python.exe $GETPIP_PY
    .\python.exe -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
}

Copy-Item -Path (Join-Path $PSScriptRoot "Scripts\\AEPython.py") -Destination (Join-Path $TARGET_ROOT "AEPython\\AEPython.py") -Force
Copy-Item -Path (Join-Path $PSScriptRoot "Scripts\\qtae.py") -Destination (Join-Path $TARGET_ROOT "AEPython\\qtae.py") -Force
Copy-Item -Path (Join-Path $PSScriptRoot "Scripts\\AEPython.jsx") -Destination (Join-Path $TARGET_ROOT "AEPython.jsx") -Force
Copy-Item (Join-Path $PSScriptRoot "Scripts\\samples") -Recurse (Join-Path $TARGET_ROOT "samples") -Force
Copy-Item (Join-Path $PSScriptRoot "README.md") -Recurse (Join-Path $TARGET_ROOT "README.md") -Force
Copy-Item (Join-Path $PSScriptRoot "README_ja.md") -Recurse (Join-Path $TARGET_ROOT "README_ja.md") -Force
Copy-Item (Join-Path $PSScriptRoot "LICENSE") -Recurse (Join-Path $TARGET_ROOT "LICENSE") -Force

Pause
