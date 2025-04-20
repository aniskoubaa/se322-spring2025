#!/bin/bash

# IoT Security Demo Runner
# This script helps to run various components of the IoT security demonstration

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${CYAN}IoT Security Demonstration Runner${NC}"
echo "--------------------------------------------------------"
echo -e "${YELLOW}This tool helps run various components of the security demo${NC}"
echo ""

function check_running_processes() {
    RUNNING_PROCS=$(ps aux | grep -E "secure_sensor_emitter|secure_web_data_server|message_sniffer|message_spoofer|mitm_attacker|security_monitor" | grep -v grep | wc -l)
    if [ $RUNNING_PROCS -gt 0 ]; then
        echo -e "${YELLOW}There are $RUNNING_PROCS demo processes already running.${NC}"
        echo "You may want to stop them before starting new ones."
        echo ""
    fi
}

function run_secure_system() {
    echo -e "${GREEN}Starting secure sensor emitter...${NC}"
    python sensors/secure_sensor_emitter.py > logs/secure_sensor.log 2>&1 &
    SENSOR_PID=$!
    echo "Sensor emitter started (PID: $SENSOR_PID)"
    
    echo -e "${GREEN}Starting secure web data server...${NC}"
    python consumers/secure_web_data_server.py > logs/secure_web_server.log 2>&1 &
    SERVER_PID=$!
    echo "Web server started (PID: $SERVER_PID)"
    
    echo -e "${YELLOW}Secure system is running. Open dashboard/index.html in your browser to view data.${NC}"
    echo "View logs in the logs/ directory."
}

function run_attack_simulation() {
    mkdir -p logs
    
    echo -e "${RED}Starting message sniffer...${NC}"
    python attack_simulation/message_sniffer.py > logs/message_sniffer.log 2>&1 &
    SNIFFER_PID=$!
    echo "Message sniffer started (PID: $SNIFFER_PID)"
    
    echo -e "${RED}Starting message spoofer...${NC}"
    python attack_simulation/message_spoofer.py > logs/message_spoofer.log 2>&1 &
    SPOOFER_PID=$!
    echo "Message spoofer started (PID: $SPOOFER_PID)"
    
    echo -e "${RED}Starting MITM attacker...${NC}"
    python attack_simulation/mitm_attacker.py > logs/mitm_attacker.log 2>&1 &
    MITM_PID=$!
    echo "MITM attacker started (PID: $MITM_PID)"
    
    echo -e "${YELLOW}Attack simulation is running. View logs in the logs/ directory.${NC}"
}

function run_security_monitor() {
    mkdir -p logs
    
    echo -e "${CYAN}Starting security monitor...${NC}"
    python security_countermeasures/security_monitor.py > logs/security_monitor.log 2>&1 &
    MONITOR_PID=$!
    echo "Security monitor started (PID: $MONITOR_PID)"
    
    echo -e "${YELLOW}Security monitor is running. View logs in logs/security_monitor.log${NC}"
}

function show_menu() {
    echo "Select an option:"
    echo "  1) Run secure IoT system (sensor + web server)"
    echo "  2) Run attack simulations"
    echo "  3) Run security monitor"
    echo "  4) View logs"
    echo "  5) Show running processes"
    echo "  6) Kill all demo processes"
    echo "  7) Open dashboard in browser"
    echo "  8) Exit"
    echo -n "Enter your choice [1-8]: "
    read choice
    
    case $choice in
        1) run_secure_system ;;
        2) run_attack_simulation ;;
        3) run_security_monitor ;;
        4) 
            if [ -d "logs" ]; then
                ls -la logs/
                echo -e "${YELLOW}To view a log, use: less logs/filename.log${NC}"
            else
                echo -e "${RED}No logs available yet${NC}"
            fi
            ;;
        5) 
            echo -e "${CYAN}Running demo processes:${NC}"
            ps aux | grep -E "secure_sensor_emitter|secure_web_data_server|message_sniffer|message_spoofer|mitm_attacker|security_monitor" | grep -v grep
            ;;
        6)
            echo -e "${RED}Killing all demo processes...${NC}"
            pkill -f "secure_sensor_emitter|secure_web_data_server|message_sniffer|message_spoofer|mitm_attacker|security_monitor"
            echo "Done"
            ;;
        7)
            echo -e "${GREEN}Opening dashboard...${NC}"
            if [ "$(uname)" == "Darwin" ]; then
                open dashboard/index.html
            elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
                xdg-open dashboard/index.html
            else
                echo -e "${RED}Could not open browser automatically. Please open dashboard/index.html manually.${NC}"
            fi
            ;;
        8) exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac
    
    echo ""
    show_menu
}

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if there are already running processes
check_running_processes

# Show menu
show_menu 