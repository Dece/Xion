from ctypes import byref, cdll, c_char_p, c_void_p, POINTER


class Xfconf:
    """Xfconf library interface."""

    def __init__(self, libxfconf="libxfconf-0.so.2",
                 libglib="libglib-2.0.so.0"):
        self.lib = cdll.LoadLibrary(libxfconf)
        self.glib = cdll.LoadLibrary(libglib)
        self.set_foreign_functions()

    def set_foreign_functions(self):
        self._ff_init = self.lib.xfconf_init
        self._ff_shutdown = self.lib.xfconf_shutdown
        self._ff_list_channels = self.lib.xfconf_list_channels
        self._ff_list_channels.restype = POINTER(c_void_p)
        self._ff_channel_get = self.lib.xfconf_channel_get
        self._ff_channel_get.argtypes = (c_char_p,)
        self._ff_channel_get.restype = c_void_p
        self._ff_channel_get_properties = self.lib.xfconf_channel_get_properties
        self._ff_channel_get_properties.argtypes = (c_void_p, c_char_p)
        self._ff_channel_get_properties.restype = c_void_p

    def init(self):
        err = c_void_p()
        if not self._ff_init(byref(err)):
            raise XfconfError("xfconf_init: error")

    def shutdown(self):
        self._ff_shutdown()

    def list_channels(self):
        channels = self._ff_list_channels()
        i = 0
        while channels[i] is not None:
            yield c_char_p(channels[i]).value.decode()
            i += 1
        self.glib.g_strfreev(channels)

    def get_channel(self, name):
        return self._ff_channel_get(name.encode())

    def list_properties(self, channel, base=None):
        table = self._ff_channel_get_properties(channel, None)
        print(table)
        self.glib.g_hash_table_destroy(table)



class XfconfError(Exception):
    pass


xfconf = Xfconf()
xfconf.init()
for channel_name in xfconf.list_channels():
    print(channel_name)
channel = xfconf.get_channel("xfce4-keyboard-shortcuts")
xfconf.list_properties(channel)
xfconf.shutdown()
