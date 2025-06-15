#!/bin/bash

# Adiciona repositório Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Atualiza e instala o driver
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18