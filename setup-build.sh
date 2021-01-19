set -eu

SCRIPT_PATH=${0%/*}
SCRIPT_NAME=${0##*/}

# Ensure script path and current working directory are not the same.
if [ "$PWD" = "$SCRIPT_PATH" ]
then
    echo "\"$SCRIPT_NAME\" should not be invoked from top-level directory" >&2
    exit 1
fi

cmake -G Ninja $@ $SCRIPT_PATH
