#! /bin/bash

case $1 in
	"install")
		cp long-distance-lamp.service /etc/systemd/system/
		systemctl enable long-distance-lamp.service
		systemctl start long-distance-lamp.service
		;;
	"uninstall")
		systemctl stop long-distance-lamp.service
		systemctl disable long-distance-lamp.service
		rm /etc/systemd/system/long-distance-lamp.service
		;;
	*)
		echo "usage $0 [install|uninstall]"
		exit 1
		;;
esac

