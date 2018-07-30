##Description:
This tool is designed to utilize [Arista eAPI](https://github.com/arista-eosplus/pyeapi) in order to make json requests and parse responses.
Main functionality includes listing active port mirroring sessions, stopping them and creating new sessions.
100G ports are supported. 

Additional functionality includes semi-automated switching of the range of source ports to one destination.
Use-case - sequential capturing of traffic from multiple sources.
Ports assigned to other monitoring sessions are skipped.

##Requirements:
Python3
pyeapi (pip install pyeapi)

##Switch requirements
User with privelege level 2 or higher is required.
Auto-enable on login for this user is **required** (aaa authorization exec default local).
See [This Arista Forum Post](https://eos.arista.com/forum/how-do-i-enable-configure-commands-via-http-api/) for how-to.

##Additional info:
Pyinstaller can be used to bake a handy executable file for Windows.
first install it using pip, then:
pyinstaller -w -F [pythonfile.py]

Py2app can be used for Mac, although not tested.

## License
[Apache 2.0](LICENSE)