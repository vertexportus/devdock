#!/usr/bin/env sh

ls -la /app
dotnet restore
dotnet build
dotnet watch run
