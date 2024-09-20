#!/bin/bash

# Function to update the OS
update_os() {
    sudo apt-get update && sudo apt-get upgrade -y
}

# Function to change network settings
change_network() {
    IP=$(dialog --inputbox "Enter new IP address:" 8 40 3>&1 1>&2 2>&3 3>&-)
    NETMASK=$(dialog --inputbox "Enter new Netmask:" 8 40 3>&1 1>&2 2>&3 3>&-)
    GATEWAY=$(dialog --inputbox "Enter new Default Gateway:" 8 40 3>&1 1>&2 2>&3 3>&-)
    
    # Update the network configuration file
    sudo bash -c "cat > /etc/netplan/01-netcfg.yaml <<EOF
network:
  version: 2
  ethernets:
    eth0:
      addresses: [$IP/$NETMASK]
      gateway4: $GATEWAY
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
EOF"
    sudo netplan apply
}

# Function to change keyboard layout
change_keyboard() {
    KEYBOARD=$(dialog --menu "Choose a keyboard layout:" 15 50 10 $(localectl list-x11-keymap-layouts | awk '{print NR, $1}') 3>&1 1>&2 2>&3 3>&-)
    sudo loadkeys $KEYBOARD
}

# Function to change timezone
change_timezone() {
    TIMEZONE=$(dialog --menu "Choose a timezone:" 15 50 10 $(timedatectl list-timezones | awk '{print NR, $1}') 3>&1 1>&2 2>&3 3>&-)
    sudo timedatectl set-timezone $TIMEZONE
}

# Main menu
while true; do
    CHOICE=$(dialog --menu "System Configuration Menu" 15 50 6 \
    1 "Update OS" \
    2 "Change Network Settings" \
    3 "Change Keyboard Layout" \
    4 "Change Timezone" \
    5 "Exit" 3>&1 1>&2 2>&3 3>&-)
    
    case $CHOICE in
        1)
            update_os
            ;;
        2)
            change_network
            ;;
        3)
            change_keyboard
            ;;
        4)
            change_timezone
            ;;
        5)
            break
            ;;
        *)
            break
            ;;
    esac
done

clear
