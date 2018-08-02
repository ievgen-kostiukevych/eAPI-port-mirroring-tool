##Description:
This tool is designed to provide a very simple GUI for the Arista EOS port mirroring functionality.
The tool is using [Arista eAPI](https://github.com/arista-eosplus/pyeapi) to make json requests and parse responses.
Main functionality includes listing active port mirroring sessions, stopping them and creating new sessions.

Additional functionality includes semi-automated switching of the range of source ports to one destination.
Use-case - sequential capturing of traffic from multiple sources.
Ports assigned to other monitoring sessions are skipped.

100G ports are supported. vEOS is supported.

##Requirements:
Python3
pyeapi (pip install pyeapi)

##Switch requirements:
User with privelege level 2 or higher is required.
Auto-enable on login for this user is **required** (aaa authorization exec default local).
See [This Arista Forum Post](https://eos.arista.com/forum/how-do-i-enable-configure-commands-via-http-api/) for how-to.

##Additional info:
Pyinstaller can be used to bake a handy executable file for Windows.
first install it using pip, then:
pyinstaller -w -F [pythonfile.py]

##License:
The tool is licensed with [Apache 2.0](LICENSE)

pyeapy module is Copyright (c) 2015, Arista Networks EOS+ All rights reserved.
Please refer to [Arista eAPI](https://github.com/arista-eosplus/pyeapi) for license details.

##Disclaimers:
As per Apache 2.0 license, the software is provided "As is", WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.
Use at your own risk.
Lab testing is ALWAYS recomended before any use for production network.