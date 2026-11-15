#!/bin/sh
# Boot a throwaway Metasploitable 2 guest and inject this lab's flag.
#
# The qcow2 is read-only and QEMU uses -snapshot, so every lab session starts
# from the same clean image. The guest is placed behind QEMU user networking
# with restricted egress; only the forwarded service ports are reachable from
# the lab network.
set -eu

LAB_FLAG="${LAB_FLAG:-OCR_missing_lab_flag}"
LAB_PROFILE="${LAB_PROFILE:-root}"

SSH_OPTS="-o StrictHostKeyChecking=no \
-o UserKnownHostsFile=/dev/null \
-o HostKeyAlgorithms=+ssh-rsa \
-o PubkeyAcceptedAlgorithms=+ssh-rsa \
-o PreferredAuthentications=password \
-o PubkeyAuthentication=no \
-o ConnectTimeout=5"

echo "[target] starting Metasploitable 2 (profile=$LAB_PROFILE)"

qemu-system-x86_64 \
    -name metasploitable2 \
    -enable-kvm -cpu host -smp 1 -m 1024 \
    -drive file=/vm/metasploitable2.qcow2,format=qcow2,if=ide,snapshot=on \
    -netdev user,id=net0,restrict=on,hostfwd=tcp:127.0.0.1:2222-:22,hostfwd=tcp:127.0.0.1:2121-:21,hostfwd=tcp:127.0.0.1:8080-:80,hostfwd=tcp:127.0.0.1:1139-:139,hostfwd=tcp:127.0.0.1:1445-:445,hostfwd=tcp:127.0.0.1:13306-:3306,hostfwd=tcp:127.0.0.1:15432-:5432,hostfwd=tcp:127.0.0.1:16200-:6200,hostfwd=tcp:127.0.0.1:18180-:8180 \
    -device e1000,netdev=net0 \
    -display none \
    -serial file:/tmp/console.log \
    -monitor unix:/tmp/monitor.sock,server,nowait &
QEMU_PID=$!

# QEMU's slirp host forwarding is reliable on loopback but not on a container
# interface in this QEMU version. socat exposes the guest ports on the lab
# network while QEMU keeps its forwards on 127.0.0.1.
SOCAT_PIDS=""
forward_port() {
    socat TCP-LISTEN:"$1",fork,reuseaddr TCP:127.0.0.1:"$2" &
    SOCAT_PIDS="$SOCAT_PIDS $!"
}
forward_port 22 2222
forward_port 21 2121
forward_port 80 8080
forward_port 139 1139
forward_port 445 1445
forward_port 3306 13306
forward_port 5432 15432
forward_port 6200 16200
forward_port 8180 18180

cleanup() {
    for pid in $SOCAT_PIDS; do
        kill "$pid" 2>/dev/null || true
    done
    kill "$QEMU_PID" 2>/dev/null || true
    wait "$QEMU_PID" 2>/dev/null || true
}
trap cleanup TERM INT

ready=0
for _ in $(seq 1 100); do
    if sshpass -p msfadmin ssh $SSH_OPTS msfadmin@127.0.0.1 true 2>/dev/null; then
        ready=1
        break
    fi
    sleep 2
done

if [ "$ready" -ne 1 ]; then
    echo "[target] guest SSH did not become ready; leaving QEMU running for inspection" >&2
    wait "$QEMU_PID"
    exit 1
fi

printf '%s\n' "$LAB_FLAG" > /tmp/msf_flag

cat > /tmp/msf_setup.sh <<'EOF'
#!/bin/sh
set -eu
PROFILE="${1:-root}"
FLAG=$(cat /tmp/msf_flag)
umask 077
case "$PROFILE" in
    web)
        install -m 0644 /tmp/msf_flag /var/www/flag.txt
        ;;
    ssh)
        install -m 0644 -o msfadmin -g msfadmin /tmp/msf_flag /home/msfadmin/flag.txt
        ;;
    mysql)
        mysql -u root <<SQL
DROP DATABASE IF EXISTS msf_lab;
CREATE DATABASE msf_lab;
USE msf_lab;
CREATE TABLE flags (id INT PRIMARY KEY, flag VARCHAR(255));
INSERT INTO flags VALUES (1, '$FLAG');
SQL
        ;;
    pivot)
        install -d -m 0755 /root/pivot
        install -m 0644 /tmp/msf_flag /root/pivot/flag.txt
        pkill -f '/root/pivot/server.py' 2>/dev/null || true
        nohup python -c "import BaseHTTPServer,SimpleHTTPServer,os; os.chdir('/root/pivot'); BaseHTTPServer.HTTPServer(('127.0.0.1',9000),SimpleHTTPServer.SimpleHTTPRequestHandler).serve_forever()" >/tmp/pivot.log 2>&1 &
        ;;
    *)
        install -m 0600 /tmp/msf_flag /root/flag.txt
        ;;
esac
rm -f /tmp/msf_flag
EOF

sshpass -p msfadmin ssh $SSH_OPTS msfadmin@127.0.0.1 "cat > /tmp/msf_flag" < /tmp/msf_flag
sshpass -p msfadmin ssh $SSH_OPTS msfadmin@127.0.0.1 "cat > /tmp/msf_setup.sh" < /tmp/msf_setup.sh
sshpass -p msfadmin ssh $SSH_OPTS msfadmin@127.0.0.1 \
    "echo msfadmin | sudo -S sh /tmp/msf_setup.sh '$LAB_PROFILE'" >/dev/null 2>&1

echo "[target] flag injected for profile=$LAB_PROFILE"
wait "$QEMU_PID"
