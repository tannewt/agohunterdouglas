agohunterdouglas
================

AgoControl integration for Hunter Douglas shades.

Prior to running, set server in the hunterdouglas.conf file to the IP of the gateway.

Hunter Douglas Protocol
-----------------------

This is the basics of the Hunter Douglas Gateway IP protocol. Each command is followed by a newline.

### Connecting
When you connect to the gateway using TCP/IP on port 522, it will return a line with a two character prefix that identifies responses to you with.

### Listing state
One can list all state from the gateway with `$dat`. This will return many lines and end with a line that starts with `upd01-`. The first two digits are client identifiers. After those prefixes there is an identifier for state. `$cs` indicates the name of a shade. `$cp` is followed by its id and its state. Other lines also exist but are not used by AgoHunterDouglas so are not yet well understood.

### Set shade state
One can set the state of a shade by sending command `$pss%s-04-%03` where the first substitution is the internal shade id and the second is the shade state. The state is a number between 0 and 255 where 0 means the shade is closed and 255 means the shade is open.
