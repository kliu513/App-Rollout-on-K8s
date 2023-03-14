#!/bin/bash
export KUBECONFIG_MAN="config-files/manager.cfg"
export NODE=$(kubectl --kubeconfig $1 get pods -n cattle-fleet-system -l app=fleet-agent -o json \
    | jq '.items | .[0].spec.nodeName')
touch clusters.txt
kubectl --kubeconfig $KUBECONFIG_MAN get clusters.fleet.cattle.io -n clusters > clusters.txt
export NODE=$(sed -e 's/^"//' -e 's/"$//' <<< "$NODE")
IFS=' ' read -ra CLUSTER <<< "$(grep $NODE clusters.txt)"
export CLUSTER
rm clusters.txt
kubectl delete clusters.fleet.cattle.io $CLUSTER --kubeconfig $KUBECONFIG_MAN -n clusters
touch log.txt
helm --kubeconfig $1 -n cattle-fleet-system uninstall fleet-agent
if [ grep "fleet-agent" log.txt ]
then
    rm log.txt
    exit 1
else
    rm log.txt
    kubectl delete namespace cattle-fleet-system
    exit 0
fi
