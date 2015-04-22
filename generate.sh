#!/bin/bash
rm -rf AppStore/scheme/*
python AppStore/GenerateAppSchemes.py
cp AppStore/scheme/extSchemeApps.json /alidata/www/web2py/applications/iam007/static/extSchemeApps.json
cp -r AppStore/scheme /alidata/www/web2py/applications/iam007/static
