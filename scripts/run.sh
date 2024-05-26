#!/bin/bash

if [ "$#" -le 1 ]; then
    echo "Usage: ./run.sh <image_type> <image>"
    exit 1
fi

case "$1" in
    "floppy")   QEMU_ARGS="${QEMU_ARGS} -fda $2"
    ;;
    "disk")     QEMU_ARGS="${QEMU_ARGS} -debugcon stdio -hda $2"
    ;;
    *)          echo "Unknown image type $1."
                exit 2
esac

/usr/bin/qemu-system-i386 $QEMU_ARGS