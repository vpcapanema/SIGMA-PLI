@echo off
echo ================================================
echo    VERIFICACAO DE CONECTIVIDADE NEO4J AURA
echo ================================================
echo.

echo 1. Testando conectividade basica...
ping -n 4 3f74966e.databases.neo4j.io

echo.
echo 2. Testando resolucao DNS...
nslookup 3f74966e.databases.neo4j.io

echo.
echo 3. Testando conectividade HTTPS (porta 443)...
telnet 3f74966e.databases.neo4j.io 443

echo.
echo 4. Testando conectividade Neo4j (porta 7687)...
telnet 3f74966e.databases.neo4j.io 7687

echo.
echo 5. Verificando configuracoes de proxy...
netsh winhttp show proxy

echo.
echo 6. Verificando firewall do Windows...
netsh advfirewall show allprofiles state

echo.
echo ================================================
echo    DIAGNOSTICO CONCLUIDO
echo ================================================
pause