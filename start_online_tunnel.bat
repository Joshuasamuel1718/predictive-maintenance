@echo off
echo =======================================================
echo 🌐 Exposing Predictive Maintenance System to the Internet...
echo =======================================================
echo.
echo Localtunnel will generate a public URL. 
echo Note: When opening the URL for the first time, you might see a 
echo 'friendly reminder' warning page. If prompted for a password/tunnel password,
echo you can find your public IP at https://localtunnel.github.io/www/ or similar,
echo or simply bypass it by clicking 'Click to Continue'.
echo.
echo Launching tunnel on port 5000...
npx localtunnel --port 5000
pause
