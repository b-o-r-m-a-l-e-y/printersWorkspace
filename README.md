# Some notes about configuration

To configure printer directly paste config into `/etc/openvp/myconfig.conf`. `.conf` is only one way. Then `systemctl enable openvpn && reboot`. Check with `ip a` and try to connect.


## Octoprint configuration

 - WebcamStreamer plugin must be installed or smth else, because first one is abandoned. On web page stream integrates in `<img>` container.