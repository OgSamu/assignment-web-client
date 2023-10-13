#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.splitlines()
        statCode = code[0].split(" ")

        return statCode[1]

    def get_headers(self,data):
        return None

    def get_body(self, data):
        resBody = data.split("\r\n\r\n")
        return resBody[1]
    
    def extractPort(self, parsedURL):
         # Return port if it exists, otherwise default to 80
        return parsedURL.port if parsedURL.port else 80
    
    def extractPath(self, parsedURL):
        return parsedURL.path if parsedURL.path else "/"
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        url_details = urllib.parse.urlparse(url)
        domain = url_details.hostname
        port_num = self.extractPort(url_details)
        endpoint = self.extractPath(url_details)

    
        request_data = f'GET {endpoint} HTTP/1.1\r\nHost: {url_details.netloc}\r\nConnection: close\r\n\r\n'

        # Establish connection, send the request, receive response, and close connection
        self.connect(domain, port_num)
        self.sendall(request_data)
        raw_response = self.recvall(self.socket)
        self.close()

        # Extract the status code and content from the response
        code = int(self.get_code(raw_response))
        body = self.get_body(raw_response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

         # Decompose the URL into its parts
        url_data = urllib.parse.urlparse(url)
        domain_name = url_data.hostname
        port_number = self.extractPort(url_data)
        route = self.extractPath(url_data)

        # Process and encode the POST parameters
        post_data = urllib.parse.urlencode(args) if args else ""
        content_length = len(post_data)

        # Build the POST request
        post_request = f'POST {route} HTTP/1.1\r\nHost: {url_data.netloc}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{post_data}'

        # Execute connection steps: connect, send the request, retrieve response, disconnect
        self.connect(domain_name, port_number)
        self.sendall(post_request)
        raw_response = self.recvall(self.socket)
        self.close()

        # Parse the received response to extract status code and body
        code = int(self.get_code(raw_response))
        body = self.get_body(raw_response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
