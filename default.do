#!/bin/sh
exec >&2
export ANSIBLE_FORCE_COLOR=True

if [ "$host" != "" ]; then
    INVENTORY="-i ${host},"
fi

if [ "$role" != "" ]; then
    VARS=--extra-vars="host_roles=${role}"
fi

set -x

case $(basename $1) in
    all)
        ansible-playbook --check --diff ${INVENTORY} ${VARS} site.yml
    ;;
    test)
        ansible-playbook --check --diff ${INVENTORY} ${VARS} site.yml
    ;;
    deploy)
        ansible-playbook ${INVENTORY} ${VARS} site.yml
    ;;
esac
