gh repo fork https://github.com/vfarcic/rancher-fleet-demo --clone
cd rancher-fleet-demo
cat repo-base.yaml
nano repo-base.yaml
git reset --hard
cat repo.yaml
nano repo.yaml
cd helm
kubectl config use-context fleet-manager
kubectl -n clusters get fleet
 1389  git add .
 1390  git commit -m "Small changes"
kubectl create secret generic basic-auth-secret -n default --type=kubernetes.io/basic-auth --from-literal=username=kliu513 --from-literal=password=
kubectl apply -f repo.yaml
kubectl -n clusters get fleet
