#!/bin/bash
set -e
nmcli connection up 'Bajourini-5G'
python wait-for-internet.py 'https://example.com'
text=$(python ./download.py)
nmcli connection up 'ATOM-PRINTER_2491'
python wait-for-internet.py 'http://192.168.4.1'
python print.py 'http://192.168.4.1' "$text"
nmcli connection up 'Bajourini-5G'
