# -*- coding: utf-8 *-*
"""
A Prometheues exporter for the nginx reverse proxy
to the Helix pendulum app. The idea here is to scrap the log of
prometheus for repeat IP offending our rules, and also geolocate IPs. 

import requests
import json

response = requests.get("https://freegeoip.app/json/122.228.19.80")

print(json.loads(response.text))
"""
