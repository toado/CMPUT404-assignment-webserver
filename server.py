#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        # Parse the (decoded) data and handle request accordingly
        # @Source: https://stackoverflow.com/a/39090882 By User "Liam Kelly"
        self.data = self.request.recv(1024).strip()
        request_header = self.data.decode().split("\r\n")
        method, path, protocol = request_header[0].split(" ")
        host, content_type = "", ""
        
        # Get the host to redirect to in a 301 error
        for header in request_header:
            if "Host" in header:
                host = header.split(": ")[1]
                break

        # print(request_header)
        # print(f"HTTP Method: {method}\nRequested Path: {path}")
        # print(f"Host: {host}\n")

        if method == "GET":
            # Link default page 
            if path[-1] == "/": 
                path += "index.html"
            
            # Serving files
            # @Source: https://stackoverflow.com/a/21153368 By User "falsetru"
            # @Source: https://stackoverflow.com/a/46109539 By User "nalyd88"
            try:
                file_path = "www" + path 
                if ".." in file_path: raise FileNotFoundError
                
                # Get content type in accordance with file type to be served
                if path.endswith("html"):
                    content_type = "text/html"
                elif path.endswith("css"):
                    content_type = "text/css"

                with open(file_path, "r") as file:
                    # Remember to close off response header (extra "\r\n")
                    self.request.sendall("HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n".format(content_type).encode())
                    self.request.sendall(file.read().encode())

            # Handle OSError subclass accordingly
            # @Source: https://docs.python.org/3/library/exceptions.html
            except FileNotFoundError:
                self.request.sendall("HTTP/1.1 404 Not Found\r\n".encode())
                self.request.sendall("\n<html><h1>404 Not Found</h1></html>".encode())
            
            # Redirecting -- general OSError because different computers had different errors for this one...
            # @Source: https://stackoverflow.com/a/50607924 By User "Dominic Roy-Stang"
            except OSError:
                self.request.sendall("HTTP/1.1 301 Moved Permanently\r\nLocation: http://{}{}/\r\n".format(host, path).encode())

        # Requirement: Return status code "405" if HTTP method not GET
        else:
            self.request.sendall("HTTP/1.1 405 Method Not Allowed\r\n".encode())
            return


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
