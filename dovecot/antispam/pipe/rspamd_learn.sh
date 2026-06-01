#!/bin/sh

case "$1" in
    ham)
	PORT=9000 ;;
    spam)
	PORT=9001 ;;
    *)
	echo "invalid class $1, must be ham or spam" >&2
	exit -1
	;;
esac

exec nc -w 30 rspamd-learn-proxy "$PORT"
