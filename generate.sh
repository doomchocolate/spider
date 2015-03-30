#!/bin/bash
python AppStore/AppStoreSpider.py generate
cp AppStore/extSchemeApps.json.1 /alidata/www/web2py/applications/iam007/static/extSchemeApps.json
cp -r AppStore/scheme /alidata/www/web2py/applications/iam007/static
