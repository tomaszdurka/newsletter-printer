import requests
import sys
def main():
    while True:
        try:
            r = requests.get(sys.argv[1])
            if r.status_code == 200:
                return
            print(r.status_code)
        except Exception as e:
            print(e)

main()