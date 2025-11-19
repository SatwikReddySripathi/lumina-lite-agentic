# AKS Troubleshooting Runbook - CVS Health

**Document ID:** TROUBLE-AKS-002  
**Version:** 2.1  
**Owner:** SRE Team

---

## Quick Diagnostic Commands

### Check Cluster Health
```bash
# Cluster status
az aks show -g <rg> -n <cluster> --query provisioningState

# Node status
kubectl get nodes -o wide

# Pod health across all namespaces
kubectl get pods --all-namespaces | grep -v Running
```

### Network Diagnostics
```bash
# Check DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# Test connectivity to external service
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- curl https://www.google.com

# View service endpoints
kubectl get endpoints -A
```

## Common Networking Issues

### DNS Resolution Failures

**Symptom:** Pods cannot resolve DNS names  
**Check:**
1. CoreDNS pods running: `kubectl get pods -n kube-system -l k8s-app=kube-dns`
2. DNS ConfigMap: `kubectl get cm coredns -n kube-system -o yaml`
3. Pod DNS config: `kubectl exec <pod> -- cat /etc/resolv.conf`

**Solutions:**
- Restart CoreDNS: `kubectl rollout restart deployment coredns -n kube-system`
- Verify VNet DNS settings point to correct servers
- Check if custom DNS server is reachable from AKS subnet
- **Form:** NET-DNS-ISSUE

### Network Policy Blocking Traffic

**Symptom:** Services cannot communicate despite being in same namespace  
**Check:**
1. Network policies: `kubectl get networkpolicies -A`
2. Describe specific policy: `kubectl describe netpol <name> -n <namespace>`

**Solutions:**
- Review policy selectors and ingress/egress rules
- Test with policy temporarily disabled (non-prod only)
- Use network policy analyzer tool (internal: cvs-netpol-analyzer)
- **Form:** NET-POLICY-REVIEW

### Load Balancer Not Assigning IP

**Symptom:** Service stuck in `<pending>` state  
**Check:**
1. Service events: `kubectl describe svc <service> -n <namespace>`
2. Subnet capacity: Verify subnet has available IPs
3. NSG rules: Check for blocks on load balancer traffic

**Solutions:**
- For internal LB: Ensure subnet annotation is correct
- For public LB: Verify static IP is from correct resource group
- Check quota limits: `az network lb list --query "length([])"`
- **Form:** NET-AKS-SUPPORT

### Ingress Controller Issues

**Symptom:** External traffic not reaching pods  
**Check:**
1. Ingress controller pods: `kubectl get pods -n ingress-nginx`
2. Ingress resource: `kubectl get ingress -A`
3. Check annotations for SSL/TLS configuration

**Solutions:**
- Verify DNS points to correct load balancer IP
- Check certificate validity for HTTPS ingress
- Review ingress controller logs: `kubectl logs -n ingress-nginx <pod>`
- **Form:** NET-INGRESS-ISSUE

## Performance Troubleshooting

### High Pod-to-Pod Latency

**Symptom:** Slow inter-service communication  
**Check:**
1. Network plugin: Verify Azure CNI is in use
2. Check for network throttling: Look at NIC metrics in Azure Portal
3. Node network performance: `kubectl top nodes`

**Solutions:**
- Ensure services are using ClusterIP (not external load balancer)
- Consider pod anti-affinity for distributed workloads
- Review NSG flow logs for bottlenecks
- **Form:** PERF-NETWORK

### Egress Throttling

**Symptom:** Timeouts when calling external APIs  
**Root Cause:** SNAT port exhaustion or firewall throttling

**Solutions:**
- Implement connection pooling in application
- Use NAT Gateway instead of default SNAT
- Request higher egress quota (Form: NET-QUOTA-INCREASE)
- Monitor SNAT port usage: Azure Monitor metric

## Security Incident Response

### Suspected Unauthorized Access

**Immediate Actions:**
1. Isolate affected pod: Apply restrictive network policy
2. Capture pod logs: `kubectl logs <pod> > incident-$(date +%s).log`
3. Get security context: `kubectl get pod <pod> -o json > pod-spec.json`
4. **CRITICAL:** File incident ticket immediately (Form: SEC-INCIDENT)

### Compliance Violation Detected

**Examples:** Public service without approval, missing NSG rules

**Actions:**
1. Document violation with screenshots
2. Temporarily restrict access if needed
3. File compliance ticket (Form: COMPLIANCE-VIOLATION)
4. Notify security team: security-incidents@cvshealth.com

## Escalation Paths

| Issue Severity | Response Time | Escalation |
|---------------|---------------|------------|
| P0 (Production Down) | 15 minutes | Page on-call SRE immediately |
| P1 (Degraded) | 1 hour | Slack #aks-support + Email |
| P2 (Non-critical) | 4 hours | Slack #aks-support |
| P3 (Question) | 1 business day | Submit form NET-AKS-SUPPORT |

## Internal Tools

- **AKS Network Analyzer:** `https://tools.cvs.internal/aks-netcheck`
- **NSG Rule Validator:** `https://tools.cvs.internal/nsg-validator`
- **VNet Topology Viewer:** Azure Portal → Network Watcher
- **Log Analytics Workspace:** `cvs-aks-prod-logs`

## Related Documentation

- Network Architecture Guide: NET-AKS-001
- Security Baseline: SEC-AKS-BASELINE
- DR Procedures: DR-AKS-001
- Monitoring Setup: MON-AKS-001