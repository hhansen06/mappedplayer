# install
1. flash armbian  	Minimal / IOT -> bookworm 	 image on sd card.
2. apt install python3 python3-pip xorg git python3-opencv python3-tk python3-pil python3-pil.imagetk python3-flask python3-flask-socketio python3-pil.imagetk

add to /etc/X11/xorg.conf.d/01-armbian-defaults.conf:
```
Section "ServerFlags"
    Option "BlankTime" "0"
EndSection
```

create service (/etc/systemd/system/x11-autologin.service) for startx (change svhh to your non root user):
```
Unit]
Description=X11 session for bernat
After=graphical.target systemd-user-sessions.service

[Service]
User=svhh
WorkingDirectory=~

PAMName=login
Environment=XDG_SESSION_TYPE=x11
TTYPath=/dev/tty8
StandardInput=tty
UnsetEnvironment=TERM

UtmpIdentifier=tty8
UtmpMode=user

StandardOutput=journal
ExecStartPre=/usr/bin/chvt 8
ExecStart=/usr/bin/startx -- vt8 -keeptty -verbose 3 -logfile /dev/null
#Restart=no
Restart=always
RestartSec=3

[Install]
WantedBy=graphical.target
```
then exec:
sudo systemctl set-default graphical.target
sudo systemctl enable x11-autologin

after reboot, you should have a black screen, with a console on the top left.
cd /opt
sudo mkdir /opt/mappedplayer
sudo chown svhh: /opt/mappedplayer
sudo mkdir /var/log/mappedplayer
sudo chown svhh: /var/log/mappedplayer
git clone https://github.com/hhansen06/mappedplayer.git
