import socket
import threading
import sys
from _thread import *

from parsedConfig import *
from requestHandler import *


def handle_connection(connection, v_hosts):
    while True:
        data = b''
        try:
            data = connection.recv(2048)
        except socket.error as exc:
            print(exc)
        resp = RequestHandler(data, v_hosts)
        # domain not found case
        if resp.get_status_message() == resp.get_status_codes()[2][2]:
            break
        try:
            if "GET" == resp.request_string[0:3]:
                connection.sendall(resp.headers.encode())
                if not resp.body == "":
                    connection.sendall(resp.body)
            elif "HEAD" == resp.request_string[0:4]:
                connection.sendall(resp.headers.encode())
            if "connection: keep-alive" in resp.request_string.lower():
                # keep connection alive for 5 seconds
                connection.settimeout(5)
        except socket.error as exc:
            print("sending error:", exc)
            sys.exit()
        if not resp.body:
            break
    connection.close()


# here I start bind sockets on each ip/port tuple, accept
# connections and handle them in threads --> ["handle_connection"]
def start_my_http(v_hosts, ip_ports, elem_num):
    server_address = (ip_ports[elem_num][0], ip_ports[elem_num][1])
    # SOCK_STREAM --> TCP connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # here we do binding ip/port
    try:
        s.bind(server_address)
    except socket.error as e:
        print("binding problem:", server_address, str(e))
        sys.exit()
    # we should be able to listen up to 1024 users
    s.listen(1024)

    while True:
        connection, address = s.accept()
        # print("connection accepted from:", address)
        # print("starting new handle_connection() thread")
        start_new_thread(handle_connection, (connection, v_hosts))


# here I parse "config.json" and start threads where -> [see "start_my_http"]
def main():
    print("hello my http :)\n")

    # here i send already read "config.json" file for parsing and get parsed object
    conf = MyConfig(open(sys.argv[1], 'r').read())

    # here i start threads on each ip/port and join them
    my_threads = []

    for elemNum in range(0, len(conf.get_ip_port())):
        new_thread = threading.Thread(target=start_my_http, args=(conf.get_my_list(), conf.get_ip_port(), elemNum))
        my_threads.append(new_thread)
        new_thread.start()

    for i in range(0, len(my_threads)):
        my_threads[i].join()


if __name__ == '__main__':
    main()
