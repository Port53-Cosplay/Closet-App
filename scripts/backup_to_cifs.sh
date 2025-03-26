#!/bin/bash

# Config
SOURCE_DB="/home/deanna/clothing_database.db"
MOUNT_POINT="/mnt/deannas_closet"
CIFS_SHARE="//192.168.14.176/Home/BKUP/DeAnnasCloset"
DATE=$(date +%F)
BACKUP_NAME="outfit_$DATE.db"

# Mount CIFS share (no creds)
mount -t cifs "$CIFS_SHARE" "$MOUNT_POINT" -o guest,uid=$(id -u),gid=$(id -g),vers=3.0

# Ensure mount succeeded
if mountpoint -q "$MOUNT_POINT"; then
    cp "$SOURCE_DB" "$MOUNT_POINT/$BACKUP_NAME"

    # Optional: keep only 4 most recent backups
    ls -1t "$MOUNT_POINT"/outfit_*.db | tail -n +5 | xargs -r rm --

    umount "$MOUNT_POINT"
else
    echo "Backup failed: Could not mount share" >> /var/log/outfit_backup.log
fi
