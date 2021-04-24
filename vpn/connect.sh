#! /usr/bin/env bash
set -euf -o pipefail

# Connects to an OpenVPN server

usage() {
    echo "usage: connect.sh
        [--username -u username=\$VPN_USERNAME]
        [--password -p password=\$VPN_PASSWORD]
        [--cert-authority -c cert_auth=\$VPN_ROOT_CERT]
        [--tls-auth-key -t tls_auth_key=\$VPN_TLS_AUTH_KEY]
        CONFIG_PATH"
}

cleanup() {
    if [[ -e openvpn.log ]]; then
        echo "Printing out openvpn logs"
        cat openvpn.log
    else
        echo "No openvpn logs to print out"
    fi
    echo "Cleaning up"
    rm -f .credentials ca.crt ta.key
    echo "Cleanup complete"
}
trap cleanup EXIT

if [[ $# -eq 0 ]]; then
    echo "No config path provided, see below"
    usage
    exit 2
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        -u | --username )
            VPN_USERNAME="$2"
            shift 2
            ;;
        -p | --password )
            VPN_PASSWORD="$2"
            shift 2
            ;;
        -c | --cert-authority )
            VPN_ROOT_CERT="$2"
            shift 2
            ;;
        -t | --tls-auth-key )
            VPN_TLS_AUTH_KEY="$2"
            shift 2
            ;;
        -h | --help )
            usage
            exit
            ;;
        -* )
            echo "Invalid option provided, see below"
            usage
            exit 2
            ;;
        * )
            CONFIG_PATH="$1"
            echo "Using config file found at $CONFIG_PATH"
            shift
            ;;
    esac
done

echo "Setting up credentials, certificate authority, and TLS auth files"
echo -e "$VPN_USERNAME\n$VPN_PASSWORD" >> .credentials
chmod 600 .credentials
echo -e "$VPN_ROOT_CERT" >> ca.crt
chmod 600 ca.crt
echo -e "$VPN_TLS_AUTH_KEY" >> ta.key
chmod 600 ta.key

echo "Initiating openvpn connection"
touch openvpn.log
sudo openvpn --config "$CONFIG_PATH" --auth-user-pass .credentials --ca ca.crt --tls-auth ta.key 1 --log-append openvpn.log --daemon
timeout 30 bash -c 'tail -n +1 -F openvpn.log | grep -q -m 1 "Initialization Sequence Completed"' || (EXIT_CODE="$?" && echo "ERROR: Unable to connect, eith exit code $EXIT_CODE" && exit "$EXIT_CODE")

echo "Connection successfully initiated!"
