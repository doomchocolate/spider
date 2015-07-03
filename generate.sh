#!/bin/bash
rm -rf /alidata/jiangerji/git/spider/AppStore/scheme/*
python /alidata/jiangerji/git/spider/AppStore/GenerateAppSchemes.py
cp /alidata/jiangerji/git/spider/AppStore/scheme/extSchemeApps.json /alidata/www/web2py/applications/iam007/static/extSchemeApps.json
cp -r /alidata/jiangerji/git/spider/AppStore/scheme /alidata/www/web2py/applications/iam007/static
