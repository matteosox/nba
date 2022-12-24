#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

usage() {
    echo "usage: connect.sh
        [--username -u username=\$VPN_USERNAME]
        [--password -p password=\$VPN_PASSWORD]
        [--cert-authority -c cert_auth=\$VPN_ROOT_CERT]
        [--tls-auth-key -t tls_auth_key=\$VPN_TLS_AUTH_KEY]
        CONFIG_PATH"
}

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
            echo "----Using config file found at $CONFIG_PATH----"
            shift
            ;;
    esac
done

cleanup() {
    echo "Cleaning up"
    rm -f .credentials ca.crt ta.key
    echo "Cleanup complete"
}
trap cleanup EXIT

echo "----Setting up credentials, certificate authority, and TLS auth files----"
echo -e "$VPN_USERNAME\n$VPN_PASSWORD" >> .credentials
chmod 600 .credentials
echo -e "$VPN_ROOT_CERT" >> ca.crt
chmod 600 ca.crt
echo -e "$VPN_TLS_AUTH_KEY" >> ta.key
chmod 600 ta.key

echo "----Initiating openvpn connection----"
touch openvpn.log
sudo openvpn --config "$CONFIG_PATH" --auth-user-pass .credentials --ca ca.crt --tls-auth ta.key 1 --log-append openvpn.log --daemon
tail --pid "$$" -n +1 -F openvpn.log &

LINE_NO=1
NOW=$(date +%s)
TIMEOUT=$((NOW + 30))
while [[ $(date +%s) -lt $TIMEOUT ]]; do
    LINES=$(tail -n +"$LINE_NO" openvpn.log)
    if echo "$LINES" | grep -q "Initialization Sequence Completed"; then
        echo "----All done!----"
        exit 0
    fi
    LINE_COUNT=$(echo "$LINES" | wc -l)
    ((LINE_NO+=LINE_COUNT))
    sleep 1
done

echo "----ERROR: Timeout reached, unable to connect----"
exit 124
