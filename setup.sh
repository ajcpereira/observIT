#!/bin/bash

# Function to update the OS
update_os() {
    sudo apt-get update && sudo apt-get upgrade -y && /usr/bin/do-release-upgrade
}

# Function for containers house keeping
house_keeping() {
    MYOUTPUT=`docker system prune -a -f; docker volume prune -a -f; docker image prune -a -f`
    # Display summary of network settings
    dialog --title "Result" --msgbox \
        "$MYOUTPUT" 10 50
}


# Function to change network settings
function change_network {

    # Create a temporary file to store the input data
    TEMP_FILE=$(mktemp)
    
    
    # Display the menu with all fields in one form
    dialog --backtitle "Network Configuration" --title "Network Input" \
        --form "\nDialog Sample Label and Values" 25 60 16 \
        "IP/CIDR:" 1 1 " . . . /" 1 25 25 30 \
        "Gateway:" 2 1 "" 2 25 25 30 \
        "DNS (Comma separated):" 3 1 "" 3 25 25 30 \
        2>$TEMP_FILE

    # Check if ESC was pressed (exit status 1 means ESC or Cancel was pressed)
    if [[ $? -ne 0 ]]; then
        return 1  # Return to the previous menu
    else
        # Read the values from the temporary file  
        readarray -t values < $TEMP_FILE
        IP_ADDRESS="${values[0]}"
        GATEWAY="${values[1]}"
        DNS="${values[2]}"

        if [ ! -z $GATEWAY ]; then
            # Clean up the temporary file
            rm -f $TEMP_FILE

            # Display summary of network settings
            dialog --title "Network Settings Summary" --msgbox \
                "IP Address: $IP_ADDRESS\nNetmask: $NETMASK\nGateway: $GATEWAY\nDNS: $DNS" 10 50
 
            # Update the network configuration file
            bash -c "cat > /tmp/network_file.tmp <<EOF
            network:
              version: 2
              ethernets:
                eth0:
                  addresses: [$IP_ADDRESS/$NETMASK]
                  gateway4: $GATEWAY
                  nameservers:
                    addresses: [$DNS]"
            sudo cp /tmp/network_file.tmp /etc/netplan/01-netcfg.yaml
            sudo netplan apply
        else
            dialog --title "Network Settings Summary" --msgbox \
                "Please fulfill the gateway" 10 50
        fi
    fi



    return 0  # Return success
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

# Function to manage containers
manage_containers() {
    CONTAINERS=$(docker ps --format "{{.Names}}" | awk '{print NR, $1}')
    if [ -z $CONTAINERS ]; then
       dialog --title "Containers Summary" --msgbox \
       "There are no containers running some manual intervention was made, please contact support" 10 50
    else
        CONTAINER=$(dialog --menu "Select a container to manage:" 15 50 10 $CONTAINERS 3>&1 1>&2 2>&3 3>&-)
    fi
    
    if [ -n "$CONTAINER" ]; then
        ACTION=$(dialog --menu "Choose an action for $CONTAINER:" 15 50 5 \
        1 "Start" \
        2 "Stop" \
        3 "Restart" 3>&1 1>&2 2>&3 3>&-)
        
        case $ACTION in
            1)
                docker start $CONTAINER
                ;;
            2)
                docker stop $CONTAINER
                ;;
            3)
                docker restart $CONTAINER
                ;;
        esac
    fi
}

# Main menu
while true; do
    CHOICE=$(dialog --menu "System Configuration Menu" 15 50 6 \
    1 "Update OS" \
    2 "Change Network Settings" \
    3 "Manage Containers" \
    4 "House Keeping for containers" \
    5 "Exit" 3>&1 1>&2 2>&3 3>&-)
    
    case $CHOICE in
        1)
            update_os
            ;;
        2)
            change_network
            ;;
        3)
            manage_containers
            ;;
        4)
            house_keeping
            ;;
        5)
            clear
            break
            ;;
        *)
            clear
            break
            ;;
    esac
done

