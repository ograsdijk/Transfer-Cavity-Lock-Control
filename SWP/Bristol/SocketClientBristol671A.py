from .SocketDeviceClient import *

class SocketClientBristol671A(SocketDeviceClient):
    """
    Socket Client class for the Bristol671A wavemeter
    """
    def __init__(self, host, port):
        super().__init__(host, port, "Bristol671A")

    def ReadValue(self):
        # request needs an action and value parameter. For now I support
        # the query action, to read a value, in this case frequency; and the
        # info action, which returns a string with all possible commands.
        # For future use a set or write command might be useful to change
        # settings from a remote device.
        return self.request('query', 'frequency')

    ############################################################################
    # below any functions can be defined for the client class, as long as the
    # appriopriate function exists on the Socket Server side
    ############################################################################


if __name__ == "__main__":
    # change to localhost for testing usage
    host, port = '127.0.0.1' ,65432#'172.28.173.109',
    sdc = SocketClientBristol671A(host, port)
    print(sdc.ReadValue())
