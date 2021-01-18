from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
from bs4 import BeautifulSoup
import requests
import json
import os



urlBase = "https://www.tcd.ie/academicregistry/exams"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        s = self.path
        dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
        if "course" in dic:
            dic['years[]'] = dic['years[]'].split(',')
            message = find_by_course(dic['course'], dic['years[]'])
            self.send_response(200)

        elif "code" in dic:
            dic['years[]'] = dic['years[]'].split(',')
            message = find_by_code(dic['code'], dic['years[]'])
            self.send_response(200)

        else:
            message = "malformed request"#
            self.send_response(500)

        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(message).encode(encoding='utf_8'))
        return


def find_by_course(course, years):
    yearReturn = {}
    for year in years:
        request = requests.get(f"{urlBase}/past-papers/annual-{year}/", auth=(os.getenv('access'), os.getenv('token')))
        soup = BeautifulSoup(request.text, 'html.parser')
        foundCourse = soup.select(f"a[name^={course}]")
        found = foundCourse[0].find_next("table")

        found = {
            elm.find_previous("td").previous_element.previous_element: f"{urlBase}{elm['href'][5:]}" 
            for elm in found.find_all("a")
        }
        yearReturn[year] = found
    return yearReturn


def find_by_code(code, years):
    yearReturn = {}
    for year in years:
        request = requests.get(f"{urlBase}/past-papers/annual-{year}/", auth=('henrym2', 'C0raTCD1'))
        soup = BeautifulSoup(request.text, 'html.parser')
        foundCode = soup.select(f'a[href*={code}]')
        found = {
            elm.find_previous("td").previous_element.previous_element: f"{urlBase}{elm['href'][5:]}" 
            for elm in foundCode
        }
        yearReturn[year] = found
    return yearReturn


# def run(server_class=HTTPServer, handler_class=handler, port=8080):
#     server_address = ('', port)
#     httpd = server_class(server_address, handler_class)
#     try:
#         httpd.serve_forever()
#     except KeyboardInterrupt:
#         pass
#     httpd.server_close()

# if __name__ == '__main__':
#     from sys import argv

#     if len(argv) == 2:
#         run(port=int(argv[1]))
#     else:
#         run()