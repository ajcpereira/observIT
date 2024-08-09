#!/bin/bash

# Function to get the list of Ethernet interfaces
get_interfaces() {
    interfaces=$(ls /sys/class/net | grep -E "^en|^eth")
    echo "$interfaces"
}

# Function to display the dialog menu
show_menu() {
    interfaces=$(get_interfaces)
    interface_array=()
    i=1
    for iface in $interfaces; do
        interface_array+=("$i" "$iface")
        ((i++))
    done

    # Use dialog to display the menu
    chosen_index=$(dialog --clear \
        --backtitle "Choose Ethernet Interface" \
        --title "Ethernet Interface Selection" \
        --menu "Select an Ethernet Interface:" 15 50 8 \
        "${interface_array[@]}" \
        2>&1 >/dev/tty)

    # Get the selected interface
    selected_interface=$(echo "$interfaces" | sed -n "${chosen_index}p")
}

# Function to get the new IP, netmask, and gateway
get_network_details() {
    new_ip=$(dialog --inputbox "Enter new IP address for $selected_interface:" 8 40 2>&1 >/dev/tty)
    new_netmask=$(dialog --inputbox "Enter netmask for $selected_interface (e.g., 255.255.255.0):" 8 40 2>&1 >/dev/tty)
    new_gateway=$(dialog --inputbox "Enter default gateway for $selected_interface:" 8 40 2>&1 >/dev/tty)
}

# Function to configure the network interface
configure_interface() {
    # Flush existing IP addresses on the selected interface
    sudo ip addr flush dev "$selected_interface"

    # Convert netmask to CIDR notation
    cidr_netmask=$(ipcalc -p "$new_ip" "$new_netmask" | awk -F= '{print $2}')

    # Assign the new IP address and netmask
    sudo ip addr add "$new_ip/$cidr_netmask" dev "$selected_interface"

    # Add the default gateway
    sudo ip route add default via "$new_gateway" dev "$selected_interface"

    # Make the changes persistent
    make_persistent
}

# Function to make the IP configuration persistent across reboots
make_persistent() {
    # Ubuntu uses Netplan for network configuration
    netplan_file="/etc/netplan/01-netcfg.yaml"

    # Backup the current configuration
    sudo cp "$netplan_file" "${netplan_file}.bak"

    # Write the new configuration
    sudo bash -c "cat > $netplan_file <<EOL
network:
  version: 2
  renderer: networkd
  ethernets:
    $selected_interface:
      dhcp4: no
      addresses:
        - $new_ip/$cidr_netmask
      gateway4: $new_gateway
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
EOL"

    # Apply the Netplan configuration
    sudo netplan apply

    dialog --msgbox "Configuration saved and made persistent." 6 50
}

# Main script execution
show_menu
get_network_details
configure_interface

# Clear the screen after dialog execution
clear

