#  coding: utf-8 
import socketserver
import os
from urllib.parse import urlparse
from http.server import SimpleHTTPRequestHandler
import re


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
        self.data = self.request.recv(1024).strip()
        request_str = self.data.decode("utf-8")
        request_lines = request_str.split("\n")

        # Parse the HTTP request
        request_lines = request_str.split('\r\n')  # Convert self.data to string first
        request_method, request_path, _ = request_lines[0].split(' ')
        deeper=0

        if request_path == '/':
            request_path +='index.html'


        if (request_path[1:].find('/')) != (-1) and (request_path[-5:] !=".html"):

            if (request_path[-1]=='/'):
                request_more = re.split(r'(/)', request_path)
                request_more.pop(0)
                request_more.pop(len(request_more)-1)
            else:
                request_more = re.split(r'(/)', request_path)

            deeper = 1
        current_directory = os.path.dirname(__file__)
        directory_contents = os.listdir(current_directory)
        directories = [item for item in directory_contents if os.path.isdir(os.path.join(current_directory, item))]

        file_path = os.path.join(current_directory, 'www', request_path[1:])

        wiki_content_path=os.path.join(current_directory, 'www')
        wiki_content = os.listdir(wiki_content_path)


        try:
            if deeper != 1:
                if request_method == "GET":
             

                    if os.path.isfile(file_path):

                        with open(file_path, 'rb') as file:
                                content = file.read()
                            
                        # Send an HTTP response with the content type set to 'text/css'
                        response = "HTTP/1.1 200 OK\r\n"
                        ending= request_path.split('.')
                        if ending[-1] == 'css':
                            response += "Content-Type: text/css\r\n"
                        elif ending[-1] == 'html' :
                            response += "Content-Type: text/html\r\n"
                        response += "Content-Length: {}\r\n".format(len(content))
                        response += "\r\n"  # Empty line to separate headers from content
                        response = response.encode("utf-8") + content
                        
                        # Send the response to the client
                        self.request.sendall(response)

                    if request_path[1:] in wiki_content :

                        has_trailing_slash = request_path[1:].endswith("/")
                        
                        if os.path.isdir(file_path):

                            redirected_url = request_path+'/'
                            response = "HTTP/1.1 301 Moved Permanently\r\n"
                            response += f"Location: {redirected_url}\r\n"
                            response += "\r\n"
                            self.request.sendall(response.encode("utf-8"))
                        else:

                            # Open and read the contents of the 'base.css' file

                            with open(file_path, 'rb') as file:
                                content = file.read()
                            
                            # Send an HTTP response with the content type set to 'text/css'
                            response = "HTTP/1.1 200 OK\r\n"
                            ending= request_path.split('.')
                            if ending[-1] == 'css':
                                response += "Content-Type: text/css\r\n"
                            elif ending[-1] == 'html' :
                                response += "Content-Type: text/html\r\n"
                            response += "Content-Length: {}\r\n".format(len(content))
                            response += "\r\n"  # Empty line to separate headers from content
                            response = response.encode("utf-8") + content
                            
                            # Send the response to the client
                            self.request.sendall(response)
                    else:
                        raise Exception("not in wiki")
                elif request_method == "PUT" or request_method == "POST" or request_method == "DELETE":

                    response = "HTTP/1.1 405 Method Not Allowed\r\n"
                    response += "Allow: GET\r\n"  # Specify allowed methods
                    response += "Content-Length: 0\r\n"
                    response += "\r\n"
                    self.request.sendall(response.encode("utf-8"))
            else:
                try:
                    copy_wiki_content_path = wiki_content_path

                    for i in request_more:
                        copy_wiki_content_path +=i

                    if copy_wiki_content_path[-1] == '/':
                        copy_wiki_content_path+='index.html'

                    with open(copy_wiki_content_path, 'rb') as file:
                        content = file.read()
    

                    # Send an HTTP response with the content type set to 'text/css'
                    response = "HTTP/1.1 200 OK\r\n"
                    ending= copy_wiki_content_path.split('.')

                    if ending[-1] == 'css':
                        response += "Content-Type: text/css\r\n"
                    elif ending[-1] == 'html' :
                        response += "Content-Type: text/html\r\n"
                    else:
                        raise Exception("not in wiki")
                    response += "Content-Length: {}\r\n".format(len(content))
                    response += "\r\n"  # Empty line to separate headers from content
                    
                    try:

                        self.request.sendall(response.encode("utf-8")+content)
                    except:
                        raise Exception("not in wiki")

                except:

                    raise Exception("not in wiki")
                
                # Send the response to the client
                self.request.sendall(response)
        except:
            not_found_html='404 Not FOUND!'

            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type: text/html\r\n"
            response += "Content-Length: {}\r\n".format(len(not_found_html))
            response += "\r\n"  # Empty line to separate headers from content
            response += not_found_html
            
            # Send the 404 response to the client
            self.request.sendall(response.encode("utf-8"))
    




if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
