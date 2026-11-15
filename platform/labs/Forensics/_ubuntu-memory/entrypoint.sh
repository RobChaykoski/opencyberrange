#!/bin/sh
# Boot a throwaway Ubuntu memory-forensics guest with a live flag process.
#
# The qcow2 is read-only and QEMU uses -snapshot. The guest is reachable only
# through the lab network SSH proxy. The flag exists only in the process
# environment; the temporary file used to stage it is deleted immediately.
set -eu

LAB_FLAG="${LAB_FLAG:-OCR_missing_memory_flag}"
SSH_OPTS="-o StrictHostKeyChecking=no \
-o UserKnownHostsFile=/dev/null \
-o PreferredAuthentications=password \
-o PubkeyAuthentication=no \
-o ConnectTimeout=5"
SSH_PASS="Analyst#2026"

if [ -r /dev/kvm ] && [ -w /dev/kvm ]; then
    echo "[memory] KVM acceleration enabled"
    set -- -enable-kvm -cpu host -smp 2
else
    echo "[memory] KVM unavailable; using TCG software emulation"
    set -- -accel tcg,thread=multi -cpu max -smp 2
fi

qemu-system-x86_64 \
    -name ubuntu-memory \
    "$@" \
    -m 2048 \
    -drive file=/vm/ubuntu-memory.qcow2,format=qcow2,if=virtio,snapshot=on \
    -netdev user,id=n1,restrict=on,hostfwd=tcp:127.0.0.1:2222-:22 \
    -device virtio-net-pci,netdev=n1 \
    -display none \
    -serial file:/tmp/console.log \
    -monitor unix:/tmp/monitor.sock,server,nowait &
QEMU_PID=$!

socat TCP-LISTEN:22,fork,reuseaddr TCP:127.0.0.1:2222 &
SOCAT_PID=$!

cleanup() {
    kill "$SOCAT_PID" 2>/dev/null || true
    kill "$QEMU_PID" 2>/dev/null || true
    wait "$QEMU_PID" 2>/dev/null || true
}
trap cleanup TERM INT

ready=0
for _ in $(seq 1 150); do
    if sshpass -p "$SSH_PASS" ssh $SSH_OPTS analyst@127.0.0.1 true 2>/dev/null; then
        ready=1
        break
    fi
    sleep 2
done

if [ "$ready" -ne 1 ]; then
    echo "[memory] guest SSH did not become ready" >&2
    wait "$QEMU_PID"
    exit 1
fi

printf '%s' "$LAB_FLAG" > /tmp/flag
cat > /tmp/mem_holder.sh <<'EOF'
#!/bin/sh
set -eu
F=$(cat /tmp/.memflag)
rm -f /tmp/.memflag
export MEMFLAG="$F"
exec sleep 3600
EOF

sshpass -p "$SSH_PASS" ssh $SSH_OPTS analyst@127.0.0.1 "cat > /tmp/.memflag" < /tmp/flag
sshpass -p "$SSH_PASS" ssh $SSH_OPTS analyst@127.0.0.1 "cat > /tmp/mem_holder.sh" < /tmp/mem_holder.sh
sshpass -p "$SSH_PASS" ssh $SSH_OPTS analyst@127.0.0.1 \
    "sudo -u analyst setsid sh /tmp/mem_holder.sh >/dev/null 2>&1 &" >/dev/null 2>&1 || true
rm -f /tmp/flag

flag_ready=0
for _ in $(seq 1 15); do
    if sshpass -p "$SSH_PASS" ssh $SSH_OPTS analyst@127.0.0.1 \
        "sudo grep -l MEMFLAG= /proc/[0-9]*/environ 2>/dev/null | head -1" \
        | grep -q .; then
        flag_ready=1
        break
    fi
    sleep 1
done
if [ "$flag_ready" -eq 1 ]; then
    echo "[memory] guest ready; live flag verified in process memory"
else
    echo "[memory] guest ready; warning: live flag process not verified" >&2
fi
wait "$QEMU_PID"
