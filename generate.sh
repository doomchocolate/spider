#!/bin/bash
python AppStore/AppStoreSpider.py generate
mv AppStore/extSchemeApps.json.1 /alidata/www/web2py/applications/iam007/static/extSchemeApps.json
