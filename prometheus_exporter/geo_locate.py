# -*- coding: utf-8 *-*
"""
WIP:
A Prometheues exporter for the nginx reverse proxy
to the Helix pendulum app. The idea here is to scrap the log of
prometheus for repeat IP offending our rules, and also geolocate IPs.
"""
import requests
import json

response = requests.get("https://freegeoip.app/json/201.95.98.150")

print(json.loads(response.text))
