
# in this class "config.json" file is parsed and put in list, where every
# element is dictionary, where are stored key - value tuples


class MyConfig:

    def __init__(self, file):

        self.vHosts = list()
        i = 0
        elem_per_host = 4

        v_host = dict()
        all_ip_port = list()

        # unique ip/port tuples
        self.uniqueIpPort = list()

        ip_port_tuple = ["", 0]
        for line in file.splitlines():

            pure_line = line.replace(" ", "").replace("\"", "").replace(",", "")
            if pure_line.startswith("vhost"):
                i = i + 1
                v_host[pure_line.split(":")[0]] = pure_line.split(":")[1]
            elif pure_line.startswith("ip"):
                i = i + 1
                v_host[pure_line.split(":")[0]] = pure_line.split(":")[1]
                ip_port_tuple[0] = pure_line.split(":")[1]
            elif pure_line.startswith("port"):
                i = i + 1
                v_host[pure_line.split(":")[0]] = int(pure_line.split(":")[1])
                ip_port_tuple[1] = int(pure_line.split(":")[1])
            elif pure_line.startswith("documentroot"):
                i = i + 1
                v_host[pure_line.split(":")[0]] = pure_line.split(":")[1]

            if i % elem_per_host == 0 and len(v_host) > 0:
                self.vHosts.append(v_host.copy())
                v_host.clear()
                all_ip_port.append(ip_port_tuple.copy())

        for ip_port in all_ip_port:
            if ip_port not in self.uniqueIpPort:
                self.uniqueIpPort.append(ip_port)

    def get_my_list(self):
        return self.vHosts

    def get_ip_port(self):
        return self.uniqueIpPort
