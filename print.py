import requests
import sys

printer_url = sys.argv[1]
text = sys.argv[2]

requests.post(printer_url, {
    'printType': 'ASCII',
    'Pdata': text
})