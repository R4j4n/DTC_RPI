#!/bin/bash

#############################################
# DTC_RPI WiFi Configuration Script
# Configure WiFi credentials for automatic
# connection management
#############################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

CONFIG_FILE="wifi_config.json"

#############################################
# Helper Functions
#############################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

#############################################
# Check NetworkManager
#############################################

check_network_manager() {
    if ! command -v nmcli &> /dev/null; then
        print_error "NetworkManager (nmcli) is not installed"
        echo ""
        print_info "Install NetworkManager with:"
        echo "  sudo apt-get update"
        echo "  sudo apt-get install network-manager"
        echo ""
        read -p "Do you want to install NetworkManager now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Installing NetworkManager..."
            sudo apt-get update
            sudo apt-get install -y network-manager
            sudo systemctl enable NetworkManager
            sudo systemctl start NetworkManager
            sleep 2
            print_success "NetworkManager installed and started"
        else
            print_warning "NetworkManager is required for WiFi management"
            exit 1
        fi
    else
        print_success "NetworkManager is installed"
    fi

    # Check if NetworkManager is running
    if ! systemctl is-active --quiet NetworkManager; then
        print_warning "NetworkManager is not running"
        read -p "Start NetworkManager now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo systemctl start NetworkManager
            sleep 2
            print_success "NetworkManager started"
        fi
    fi
}

#############################################
# Show Current Configuration
#############################################

show_current_config() {
    if [ -f "$CONFIG_FILE" ]; then
        print_header "Current WiFi Configuration"

        # Parse and display networks
        if command -v python3 &> /dev/null; then
            python3 << EOF
import json
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
        networks = config.get('networks', [])

    if networks:
        for i, net in enumerate(networks, 1):
            ssid = net.get('ssid', 'N/A')
            priority = net.get('priority', 'N/A')
            # Don't show password
            print(f"  {i}. SSID: {ssid}")
            print(f"     Priority: {priority}")
            print(f"     Password: {'*' * 8}")
            print()
    else:
        print("  No networks configured")
except Exception as e:
    print(f"  Error reading config: {e}")
EOF
        else
            cat "$CONFIG_FILE"
        fi
        echo ""
    else
        print_info "No WiFi configuration file found"
        echo ""
    fi
}

#############################################
# Show Available Networks
#############################################

show_available_networks() {
    print_header "Scanning for Available WiFi Networks"

    print_info "Scanning..."

    if nmcli device wifi list 2>/dev/null | head -20; then
        echo ""
        print_success "Scan complete"
    else
        print_warning "Could not scan for networks"
        print_info "Make sure WiFi adapter is enabled"
    fi

    echo ""
}

#############################################
# Show Current WiFi Status
#############################################

show_wifi_status() {
    print_header "Current WiFi Status"

    # Get current SSID
    CURRENT_SSID=$(iwgetid -r 2>/dev/null || echo "")

    if [ -n "$CURRENT_SSID" ]; then
        print_success "Connected to: $CURRENT_SSID"

        # Get IP address
        IP_ADDR=$(ip -4 addr show wlan0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "")
        if [ -n "$IP_ADDR" ]; then
            echo "  IP Address: $IP_ADDR"
        fi

        # Get signal strength
        SIGNAL=$(iwconfig wlan0 2>/dev/null | grep -oP '(?<=Signal level=)-?\d+' || echo "")
        if [ -n "$SIGNAL" ]; then
            echo "  Signal Level: ${SIGNAL} dBm"
        fi
    else
        print_warning "Not connected to WiFi"
    fi

    echo ""
}

#############################################
# Configure WiFi Networks
#############################################

configure_wifi() {
    print_header "WiFi Network Configuration"

    # Backup existing config if it exists
    if [ -f "$CONFIG_FILE" ]; then
        BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%s)"
        cp "$CONFIG_FILE" "$BACKUP_FILE"
        print_info "Existing configuration backed up to $BACKUP_FILE"
        echo ""
    fi

    # Array to store network configurations
    declare -a NETWORKS

    # Ask how many networks to configure
    echo -e "${BLUE}How many WiFi networks do you want to configure?${NC}"
    echo "  (You can configure multiple networks as backups)"
    read -p "Enter number (1-5, default: 1): " NUM_NETWORKS
    NUM_NETWORKS=${NUM_NETWORKS:-1}

    # Validate input
    if ! [[ "$NUM_NETWORKS" =~ ^[1-5]$ ]]; then
        print_warning "Invalid number, using default (1)"
        NUM_NETWORKS=1
    fi

    echo ""

    # Collect network information
    for i in $(seq 1 $NUM_NETWORKS); do
        print_info "Configuring Network #$i"
        echo ""

        # Get SSID
        read -p "  WiFi SSID (network name): " SSID
        while [ -z "$SSID" ]; do
            print_warning "SSID cannot be empty"
            read -p "  WiFi SSID (network name): " SSID
        done

        # Get Password (hidden input)
        read -s -p "  WiFi Password: " PASSWORD
        echo ""
        while [ -z "$PASSWORD" ]; do
            print_warning "Password cannot be empty"
            read -s -p "  WiFi Password: " PASSWORD
            echo ""
        done

        # Confirm password
        read -s -p "  Confirm Password: " PASSWORD_CONFIRM
        echo ""

        while [ "$PASSWORD" != "$PASSWORD_CONFIRM" ]; do
            print_warning "Passwords do not match!"
            read -s -p "  WiFi Password: " PASSWORD
            echo ""
            read -s -p "  Confirm Password: " PASSWORD_CONFIRM
            echo ""
        done

        # Get Priority
        if [ $NUM_NETWORKS -gt 1 ]; then
            read -p "  Priority (1=highest, default: $i): " PRIORITY
            PRIORITY=${PRIORITY:-$i}
        else
            PRIORITY=1
        fi

        # Escape special characters in SSID and password for JSON
        SSID_ESCAPED=$(echo "$SSID" | sed 's/"/\\"/g' | sed "s/'/\\'/g")
        PASSWORD_ESCAPED=$(echo "$PASSWORD" | sed 's/"/\\"/g' | sed "s/'/\\'/g")

        # Store network info
        NETWORKS+=("{\"ssid\": \"$SSID_ESCAPED\", \"password\": \"$PASSWORD_ESCAPED\", \"priority\": $PRIORITY}")

        echo ""
        print_success "Network #$i configured: $SSID (Priority: $PRIORITY)"
        echo ""
    done

    # Create JSON configuration
    print_info "Creating $CONFIG_FILE..."

    # Join array elements with commas
    NETWORKS_JSON=$(IFS=,; echo "${NETWORKS[*]}")

    # Write JSON file
    cat > "$CONFIG_FILE" << EOF
{
  "networks": [
    $NETWORKS_JSON
  ]
}
EOF

    # Secure the file
    chmod 600 "$CONFIG_FILE"

    print_success "WiFi configuration saved to $CONFIG_FILE"
    print_info "File permissions set to 600 (owner read/write only)"
    echo ""
}

#############################################
# Test WiFi Connection
#############################################

test_connection() {
    print_header "Test WiFi Connection"

    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "No WiFi configuration file found"
        print_info "Please configure WiFi first"
        return
    fi

    # Get first network from config
    if command -v python3 &> /dev/null; then
        NETWORK_INFO=$(python3 << EOF
import json
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
        networks = config.get('networks', [])

    if networks:
        net = networks[0]
        print(f"{net.get('ssid', '')}|||{net.get('password', '')}")
except:
    pass
EOF
        )

        if [ -n "$NETWORK_INFO" ]; then
            IFS='|||' read -r TEST_SSID TEST_PASSWORD <<< "$NETWORK_INFO"

            print_info "Testing connection to: $TEST_SSID"
            echo ""

            print_info "Attempting to connect..."
            if sudo nmcli device wifi connect "$TEST_SSID" password "$TEST_PASSWORD" 2>&1; then
                sleep 3

                CURRENT_SSID=$(iwgetid -r 2>/dev/null || echo "")
                if [ "$CURRENT_SSID" = "$TEST_SSID" ]; then
                    print_success "Successfully connected to $TEST_SSID!"

                    # Get IP
                    IP_ADDR=$(ip -4 addr show wlan0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "")
                    if [ -n "$IP_ADDR" ]; then
                        echo "  IP Address: $IP_ADDR"
                    fi

                    # Test internet connectivity
                    print_info "Testing internet connectivity..."
                    if ping -c 3 -W 2 8.8.8.8 &>/dev/null; then
                        print_success "Internet connection working!"
                    else
                        print_warning "Connected to WiFi but no internet access"
                    fi
                else
                    print_warning "Connection attempt completed but not connected"
                fi
            else
                print_error "Failed to connect to $TEST_SSID"
                print_info "Please check your SSID and password"
            fi
        else
            print_error "Could not read network configuration"
        fi
    else
        print_error "Python3 is required for this feature"
    fi

    echo ""
}

#############################################
# Delete Configuration
#############################################

delete_config() {
    print_header "Delete WiFi Configuration"

    if [ ! -f "$CONFIG_FILE" ]; then
        print_info "No configuration file to delete"
        return
    fi

    print_warning "This will delete your WiFi configuration!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Create backup first
        BACKUP_FILE="${CONFIG_FILE}.deleted.$(date +%s)"
        mv "$CONFIG_FILE" "$BACKUP_FILE"
        print_success "Configuration deleted"
        print_info "Backup saved to $BACKUP_FILE"
    else
        print_info "Deletion cancelled"
    fi

    echo ""
}

#############################################
# Main Menu
#############################################

show_menu() {
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║    DTC_RPI WiFi Configuration Tool    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "1) Show current WiFi status"
    echo "2) Scan for available networks"
    echo "3) Configure WiFi credentials"
    echo "4) View current configuration"
    echo "5) Test WiFi connection"
    echo "6) Delete configuration"
    echo "7) Install/check NetworkManager"
    echo "0) Exit"
    echo ""
}

#############################################
# Main Program
#############################################

main() {
    clear

    print_header "DTC_RPI WiFi Setup"
    print_info "Location: $SCRIPT_DIR"
    print_info "Config file: $CONFIG_FILE"
    echo ""

    # Check for NetworkManager on first run
    check_network_manager

    while true; do
        echo ""
        show_menu

        read -p "Select an option: " choice
        echo ""

        case $choice in
            1)
                show_wifi_status
                read -p "Press Enter to continue..."
                clear
                ;;
            2)
                show_available_networks
                read -p "Press Enter to continue..."
                clear
                ;;
            3)
                configure_wifi
                read -p "Press Enter to continue..."
                clear
                ;;
            4)
                show_current_config
                read -p "Press Enter to continue..."
                clear
                ;;
            5)
                test_connection
                read -p "Press Enter to continue..."
                clear
                ;;
            6)
                delete_config
                read -p "Press Enter to continue..."
                clear
                ;;
            7)
                check_network_manager
                read -p "Press Enter to continue..."
                clear
                ;;
            0)
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option"
                read -p "Press Enter to continue..."
                clear
                ;;
        esac
    done
}

# Run main program
main
