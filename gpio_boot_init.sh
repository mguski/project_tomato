#! /bin/bash 
gpio -g mode 17 out
gpio -g write 17 0
exit 0

# copy this to /etc/init.d
# run sudo update-rc.d gpio_boot_init.sh defaults

