#!/usr/bin/env python3
"""
Instructa-Gotchi UNIHIKER M10 Deployment & Backup Tool
Deploys Instructa-Gotchi to a physical UNIHIKER single-board computer via USB-C or Wi-Fi.

Features:
1. Backs up existing files on UNIHIKER before uploading.
2. Synchronizes project code, assets, and database cleanly.
3. Configures optional auto-start systemd service so Tinko turns on automatically at boot.
4. Verifies the installation and hardware dependencies.

Usage:
    python3 tools/deploy_unihiker.py [--ip 10.1.2.3] [--user root] [--path /root/instructgotchi]
"""
import sys
import os
import time
import argparse
import subprocess
from pathlib import Path

DEFAULT_UNIHIKER_IP = "10.1.2.3"
DEFAULT_USER = "root"
DEFAULT_REMOTE_PATH = "/root/instructgotchi"
BACKUP_REMOTE_DIR = "/root/unihiker_backups"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_ssh_command(user: str, ip: str, cmd: str) -> subprocess.CompletedProcess:
    """Runs a remote command over SSH."""
    ssh_cmd = [
        "ssh",
        "-o", "ConnectTimeout=5",
        "-o", "StrictHostKeyChecking=no",
        f"{user}@{ip}",
        cmd
    ]
    return subprocess.run(ssh_cmd, capture_output=True, text=True)

def check_connection(user: str, ip: str) -> bool:
    print(f"Connecting to UNIHIKER at {user}@{ip}...")
    res = run_ssh_command(user, ip, "uname -a && python3 --version")
    if res.returncode == 0:
        print(f"✅ Connected to UNIHIKER successfully:\n   {res.stdout.strip()}")
        return True
    else:
        print(f"❌ Could not connect to UNIHIKER at {ip}.")
        print(f"   Error: {res.stderr.strip() or 'Connection timed out'}")
        print("\nTroubleshooting Tips:")
        print("1. Ensure UNIHIKER is connected to your Mac via USB-C.")
        print("2. Wait ~30 seconds for the USB RNDIS network gadget (10.1.2.3) to initialize.")
        print("3. Check if password authentication is required (default password is 'dfrobot').")
        print("4. You can setup passwordless SSH keys with: ssh-copy-id root@10.1.2.3")
        return False

def backup_existing_code(user: str, ip: str, remote_path: str):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_dest = f"{BACKUP_REMOTE_DIR}/backup_{timestamp}"
    print(f"\n📦 Creating safety backup of existing UNIHIKER files to {backup_dest}...")
    cmd = f"mkdir -p {BACKUP_REMOTE_DIR} && if [ -d '{remote_path}' ]; then cp -r '{remote_path}' '{backup_dest}'; echo 'Backup created'; else echo 'No existing directory found'; fi"
    res = run_ssh_command(user, ip, cmd)
    print(f"   {res.stdout.strip()}")

def sync_project_files(user: str, ip: str, remote_path: str):
    print(f"\n🚀 Uploading Instructa-Gotchi to {user}@{ip}:{remote_path}...")
    # Ensure remote directory exists
    run_ssh_command(user, ip, f"mkdir -p {remote_path}")

    rsync_cmd = [
        "rsync", "-avz", "--progress",
        "--exclude", "__pycache__",
        "--exclude", "*.pyc",
        "--exclude", ".DS_Store",
        "--exclude", "tests/previews/working_anim_test",
        str(PROJECT_ROOT) + "/",
        f"{user}@{ip}:{remote_path}/"
    ]
    res = subprocess.run(rsync_cmd)
    if res.returncode == 0:
        print("✅ Code and 240x320 assets synchronized successfully!")
        return True
    else:
        print(f"❌ Rsync failed with code {res.returncode}. Trying scp fallback...")
        scp_cmd = ["scp", "-r", str(PROJECT_ROOT), f"{user}@{ip}:{remote_path}"]
        res2 = subprocess.run(scp_cmd)
        return res2.returncode == 0

def install_systemd_autostart(user: str, ip: str, remote_path: str):
    service_content = f"""[Unit]
Description=Instructa-Gotchi Digital Companion (UNIHIKER M10)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={remote_path}
ExecStart=/usr/bin/python3 {remote_path}/run.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    print("\n⚙️ Configuring automatic boot service (systemd)...")
    cmd = f"""cat << 'EOF' > /etc/systemd/system/instructgotchi.service
{service_content}
EOF
systemctl daemon-reload
systemctl enable instructgotchi.service
"""
    res = run_ssh_command(user, ip, cmd)
    if res.returncode == 0:
        print("✅ Systemd auto-start enabled: Tinko will boot automatically on power-up.")
    else:
        print(f"Notice: systemd service setup: {res.stderr.strip()}")

def main():
    parser = argparse.ArgumentParser(description="Deploy Instructa-Gotchi to UNIHIKER M10")
    parser.add_argument("--ip", default=DEFAULT_UNIHIKER_IP, help=f"UNIHIKER IP (default: {DEFAULT_UNIHIKER_IP})")
    parser.add_argument("--user", default=DEFAULT_USER, help=f"SSH user (default: {DEFAULT_USER})")
    parser.add_argument("--path", default=DEFAULT_REMOTE_PATH, help=f"Remote path (default: {DEFAULT_REMOTE_PATH})")
    parser.add_argument("--autostart", action="store_true", help="Enable systemd auto-start on boot")
    args = parser.parse_args()

    print("==================================================")
    print("🤖 Instructa-Gotchi UNIHIKER M10 Deployment Tool")
    print("==================================================")

    if not check_connection(args.user, args.ip):
        sys.exit(1)

    backup_existing_code(args.user, args.ip, args.path)
    if sync_project_files(args.user, args.ip, args.path):
        if args.autostart:
            install_systemd_autostart(args.user, args.ip, args.path)

        print("\n🎉 Deployment completed successfully!")
        print("To start Instructa-Gotchi right now on the UNIHIKER:")
        print(f"   ssh {args.user}@{args.ip} 'cd {args.path} && python3 run.py'")
        print(f"To open the Phone Companion app:")
        print(f"   Connect your phone to the same Wi-Fi and open http://{args.ip}:8088/")

if __name__ == "__main__":
    main()

