#! /usr/bin/env bash
set -euf -o pipefail

# Connects to an OpenVPN server

usage()
{
    echo "usage: ./connect.sh [--username -u \$VPN_USERNAME] [--password -p \$VPN_PASSWORD] [--cert-authority -c \$VPN_ROOT_CERT] [--tls-auth-key -t \$VPN_TLS_AUTH_KEY] CONFIG_PATH"
}

while [[ $# -gt 1 ]]; do
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
        * )
            usage
            exit 2
            ;;
    esac
done

CONFIG_PATH="$1"
echo "Setting config path to $CONFIG_PATH"

echo "Setting up credentials, certificate authority, and TLS auth files"
echo -e "$VPN_USERNAME\n$VPN_PASSWORD" >> .credentials
chmod 600 .credentials
echo -e "$VPN_ROOT_CERT" >> ca.crt
chmod 600 ca.crt
echo -e "$VPN_TLS_AUTH_KEY" >> ta.key
chmod 600 ta.key

echo "----Initiating openvpn connection----"
sudo openvpn --config $CONFIG_PATH --auth-user-pass .credentials --ca ca.crt --tls-auth ta.key 1 --daemon --log openvpn.log

timeout 15 tail -F openvpn.log & timeout 15 bash -c 'tail -F openvpn.log | grep -q -m 1 "Initialization Sequence Completed"'

echo "----All done!----"
