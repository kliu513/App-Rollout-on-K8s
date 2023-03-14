#!/bin/bash
export KUBECONFIG_MAN="config-files/manager.cfg"
touch log.txt
kubectl --kubeconfig $KUBECONFIG_MAN -n clusters get clusters.fleet.cattle.io > log.txt
n_lines_before=`wc --lines < log.txt`
helm -n cattle-fleet-system install --create-namespace --wait \
    --kubeconfig $2 \
    --set-string labels.group=$1 \
    --values config-files/values.yaml \
    fleet-agent https://github.com/rancher/fleet/releases/download/v0.5.0/fleet-agent-0.5.0.tgz
kubectl --kubeconfig $KUBECONFIG_MAN -n clusters get clusters.fleet.cattle.io > log.txt
n_lines_after=`wc --lines < log.txt`
rm log.txt
if [ $n_lines_after -gt $n_lines_before ]
then
    exit 0
else
    exit 1
fi
