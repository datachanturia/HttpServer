
import datetime
import os
import magic


class RequestHandler:

    def __init__(self, request, v_hosts):
        # required headers for response
        self.headers = ["server", "date", "content-length", "content-type", "etag"]
        self.status_codes = [["200", "OK"],
                             ["206", "Partial Content"],
                             ["404", "Not Found", "REQUESTED DOMAIN NOT FOUND"],
                             ["416", "Range Not Satisfiable"]]
        self.headers = ""
        self.body = b''
        self.document_root = ""

        self.request_string = request.decode()
        self.ranges = []

        # here we check "404 REQUESTED DOMAIN NOT FOUND" case
        if self.status_domain_not_found(v_hosts):
            return

        self.path = self.document_root + self.request_string.splitlines()[0].split(" ")[1]
        # here we check "404 Not Found" case
        if self.status_not_found():
            return

        file = open(self.path, "rb")
        file.seek(0)
        data = file.read()

        self.body = data

        # here we check "416 Range Not Satisfiable" case
        if self.status_range_not_satisfiable():
            return
        # here we check "206 Partial Content" case
        if self.status_partial_content():
            return

        # else.. everything's okay "200 OK" case
        self.headers = ""
        self.headers += "HTTP/1.1 " + self.status_codes[0][0] + " " + self.status_codes[0][1] + " \r\n"
        self.headers += "server: MyFirst HTTP Server 1.0\r\n"
        self.headers += "date: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\r\n"
        if "connection: keep-alive" in self.request_string.lower():
            self.headers += "connection: keep-alive\r\n"
            self.headers += "keep-alive: timeout=5, max=1000\r\n"
        self.headers += "content-length: " + str(len(self.body)) + "\r\n"
        self.headers += "content-type: " + magic.from_buffer(self.body, mime=True) + "\r\n"
        self.headers += "accept-ranges: bytes\r\n"
        self.headers += "etag: \"\"\r\n"
        self.headers += "\r\n"
        self.status_message = self.status_codes[0][1]

    # 404 REQUESTED DOMAIN NOT FOUND
    def status_domain_not_found(self, v_hosts):
        self.status_message = self.status_codes[2][2]
        for v_host in v_hosts:
            if "host: " + v_host.get("vhost") in self.request_string.lower():
                self.status_message = ""
                self.document_root = v_host.get("documentroot")
        if self.get_status_message() == self.status_codes[2][2]:
            self.headers = "HTTP/1.1 " + self.status_codes[2][0] + " " + self.status_codes[2][2] + "\r\n"
            self.headers += "server: MyFirst HTTP Server 1.0\r\n"
            self.headers += "date: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\r\n"
            if "connection: keep-alive" in self.request_string.lower():
                self.headers += "connection: keep-alive\r\n"
                self.headers += "keep-alive: timeout=5, max=1000\r\n"
            self.headers += "content-length: " + str(len(self.body)) + "\r\n"
            self.headers += "content-type: " + magic.from_buffer(self.body, mime=True) + "\r\n"
            self.headers += "accept-ranges: bytes\r\n"
            self.headers += "etag: \"\"\r\n"
            self.headers += "\r\n"
            return True
        return False

    # 404 Not Found
    def status_not_found(self):
        if not os.path.exists(self.path.replace("%20", " ")):
            self.headers = "HTTP/1.1 " + self.status_codes[2][0] + " " + self.status_codes[2][1] + "\r\n"
            self.headers += "server: MyFirst HTTP Server 1.0\r\n"
            self.headers += "date: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\r\n"
            if "connection: keep-alive" in self.request_string.lower():
                self.headers += "connection: keep-alive\r\n"
                self.headers += "keep-alive: timeout=5, max=1000\r\n"
            self.headers += "content-length: " + str(len(self.body)) + "\r\n"
            self.headers += "content-type: " + magic.from_buffer(self.body, mime=True) + "\r\n"
            self.headers += "accept-ranges: bytes\r\n"
            self.headers += "etag: \"\"\r\n"
            self.headers += "\r\n"
            return True
        self.path = self.path.replace("%20", " ")
        return False

    # 206 Partial Content
    def status_partial_content(self):
        if "range: bytes=" in self.request_string.lower():
            self.body = self.body[self.ranges[0]:self.ranges[1]+1]
            self.headers += "HTTP/1.1 " + self.status_codes[0][0] + " " + self.status_codes[0][1] + " \r\n"
            self.headers += "server: MyFirst HTTP Server 1.0\r\n"
            self.headers += "date: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\r\n"
            if "connection: keep-alive" in self.request_string.lower():
                self.headers += "connection: keep-alive\r\n"
                self.headers += "keep-alive: timeout=5, max=1000\r\n"
            self.headers += "content-length: " + str(len(self.body)) + "\r\n"
            self.headers += "content-type: " + magic.from_buffer(self.body, mime=True) + "\r\n"
            self.headers += "accept-ranges: bytes\r\n"
            self.headers += "etag: \"\"\r\n"
            self.headers += "\r\n"
            return True
        return False

    # 416 Range Not Satisfiable
    def status_range_not_satisfiable(self):
        line = ""
        continue_method = False
        for line in self.request_string.lower().splitlines():
            if "range: bytes=" in line:
                continue_method = True
                break
        if not continue_method:
            return False

        line = line.replace("\r\n", "").replace("range: bytes=", "")
        line = line.split(",")
        for pair in line:
            i = 0
            for range_elem in pair.split("-"):
                if range_elem == "" and i % 2 == 0:
                    range_elem = "0"
                elif range_elem == "" and i % 2 == 1:
                    range_elem = str(len(self.body) - 1)
                self.ranges.append(int(range_elem))
                i = i + 1
                if int(range_elem) >= len(self.body):
                    self.headers = "HTTP/1.1 " + self.status_codes[3][0] + " " + self.status_codes[3][1] + "\r\n"
                    self.headers += "server: MyFirst HTTP Server 1.0\r\n"
                    self.headers += "date: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\r\n"
                    if "connection: keep-alive" in self.request_string.lower():
                        self.headers += "connection: keep-alive\r\n"
                        self.headers += "keep-alive: timeout=5, max=1000\r\n"
                    self.headers += "content-length: " + str(len(self.body)) + "\r\n"
                    self.headers += "content-type: " + magic.from_buffer(self.body, mime=True) + "\r\n"
                    self.headers += "accept-ranges: bytes\r\n"
                    self.headers += "etag: \"\"\r\n"
                    self.headers += "\r\n"
                    return True
        return False

    def get_status_message(self):
        return self.status_message

    def get_status_codes(self):
        return self.status_codes
