from SocketDeviceServer import *
from Bristol671A import *


class Device(threading.Thread):
    """
    Separate thread for reading from the device, to not block the socket request
    calls.
    """
    def __init__(self, dt, server, device, dev_kwargs):
        threading.Thread.__init__(self)
        self.data = server.data
        # comment line below for testing
        # self.device = device(**dev_kwargs)
        self.dt = dt

    def run(self):
        while True:
            # comment line below for testing
            # self.data['frequency']['seed1'] = (time.time(), self.device.MeasureFrequency())
            # uncomment line below for testing
            self.data['frequency'] = (time.time(), {'seed1' : 275.293+random.random()/1000})

            time.sleep(self.dt)

class SocketServerBristol671A(SocketDeviceServer):
    """
    Socket Server class for Bristol671A wavemeter
    """
    def __init__(self, host, port, dev_kwargs):
        self.data = {'frequency':{}}
        self.device = Device(0.2, self, Bristol671A, dev_kwargs)
        super().__init__(host, port)

    @staticmethod
    def create_response(message):
        """
        Queries for the Socket Server
        Method of the ServerMessage class, but need to define different queries
        per device hence pulles into the SocketServerDevice parent class, to be
        defined for each separate device
        Here a query and info action are defined: in case of a query the to be
        queried value needs to be defined, which exists in the self.data
        dictionary. For this example only the frequency is pulled from the
        device.
        """
        action = message.request.get("action")
        if action == "query":
            query = message.request.get("value")
            print(message)
            if message.data.get(query):
                content = {"result": message.data.get(query)}
                # content={"result":self.device.data}
            else:
                content = {"error": f'No match for "{query}".'}
        elif action == "info":
            content = {"result": "Socket server for Bristol671A\n"+
                                 "Valid command are: \n"+
                                 "query: query a value from the device"}
        else:
            content = {"error": f'invalid action "{action}".'}
        content_encoding = "utf-8"
        response = {
            "content_bytes": message._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }

        return response

if __name__ == "__main__":
    # host = '' accepts connections from everywhere, use 'localhost' for no
    # external access
    host, port = '', 65432
    device_kwargs = {'time_offset': 0,
                     'connection': {'telnet_address': '10.199.199.1', 'telnet_port': 23}}
    print('Starting SocketServerBristol671A')
    sds = SocketServerBristol671A(host, port, device_kwargs)
    sds.run()
