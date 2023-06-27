# Configurar tap0
sudo tunctl -u saguira
sudo ifconfig tap0 192.168.0.10/24 up

# Agregar las direcciones ip
sudo route add -net 10.10.10.0 netmask 255.255.255.0 gw 192.168.0.9 dev tap0
sudo route add -net 20.20.20.0 netmask 255.255.255.0 gw 192.168.0.9 dev tap0
sudo route add -net 30.30.30.0 netmask 255.255.255.0 gw 192.168.0.9 dev tap0
sudo route add -net 192.168.0.0 netmask 255.255.255.0 gw 192.168.0.9 dev tap0
sudo route add -net 40.40.40.0 netmask 255.255.255.0 gw 192.168.0.9 dev tap0
sudo route add -net 192.168.1.0 netmask 255.255.255.0 gw 192.168.0.9 dev tap0
