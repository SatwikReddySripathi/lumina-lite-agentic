# AKS Networking Guide - CVS Health Internal

**Document ID:** NET-AKS-001  
**Last Updated:** November 2024  
**Owner:** Cloud Infrastructure Team

---

## Overview

This guide covers Azure Kubernetes Service (AKS) networking configurations approved for CVS Health production workloads.

## Network Architecture

### Virtual Network (VNet) Configuration

**Standard Setup:**
- Primary VNet: `10.100.0.0/16`
- AKS Subnet: `10.100.1.0/24` (256 IPs)
- Internal Services Subnet: `10.100.2.0/24`
- Gateway Subnet: `10.100.255.0/27`

**Requirements:**
- All production AKS clusters MUST use Azure CNI (not kubenet)
- Enable Network Policy (Azure Network Policy or Calico)
- Reserve at least /24 subnet for AKS nodes

### Network Security Groups (NSG)

**Inbound Rules (Priority Order):**

1. **Allow Azure Load Balancer** (Priority: 100)
   - Source: AzureLoadBalancer
   - Destination: Any
   - Ports: Any
   - Protocol: Any

2. **Allow Internal VNet Traffic** (Priority: 200)
   - Source: VirtualNetwork
   - Destination: VirtualNetwork
   - Ports: 443, 80, 22
   - Protocol: TCP

3. **Allow Azure Container Registry** (Priority: 300)
   - Source: AKS Subnet
   - Destination: Service Tag: AzureContainerRegistry
   - Port: 443
   - Protocol: TCP

4. **Deny All Other Inbound** (Priority: 4096)

**Outbound Rules:**

1. **Allow Azure Services** (Priority: 100)
   - Required service tags: AzureCloud, AzureMonitor, AzureActiveDirectory
   - Port: 443

2. **Allow Container Registry** (Priority: 200)
   - Destination: mcr.microsoft.com, *.azurecr.io
   - Port: 443

### Private Link Configuration

**For Production Clusters:**
- Enable Private Endpoint for AKS API server
- Whitelist IP ranges: `10.0.0.0/8` (internal), VPN gateway ranges
- Use Azure Private DNS zones for name resolution

**DNS Configuration:**
- Private zone: `privatelink.{region}.azmk8s.io`
- Link to Hub VNet for cross-region access

## Load Balancer Setup

### Internal Load Balancer

**Configuration:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: internal-app
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-internal: "true"
spec:
  type: LoadBalancer
  loadBalancerIP: 10.100.2.10
```

### Public Load Balancer (DMZ Only)

**Requirements:**
- Only allowed in DMZ AKS clusters
- Must use static public IP from reserved pool
- Requires Security review ticket (Form: SEC-LB-001)

## Common Issues & Solutions

### Issue 1: Pods Cannot Pull Images
**Symptoms:** ImagePullBackOff errors  
**Root Cause:** NSG blocking ACR access  
**Solution:** 
- Verify NSG rule for AzureContainerRegistry service tag
- Check if subnet has route table overriding default routes
- Submit ticket: NET-AKS-SUPPORT

### Issue 2: Service Not Reachable
**Symptoms:** Timeout connecting to service  
**Root Cause:** Missing NSG rules for load balancer probe  
**Solution:**
- Add AzureLoadBalancer rule (priority < 1000)
- Verify health probe configuration
- Check network policy if using Calico

### Issue 3: Cross-Cluster Communication Fails
**Symptoms:** Cannot reach services in another AKS cluster  
**Root Cause:** VNet peering not configured  
**Solution:**
- Submit VNet peering request (Form: NET-PEER-REQ)
- Ensure NSGs allow traffic from peer VNet CIDR
- Update route tables if using hub-spoke topology

## Security Best Practices

1. **Always use Azure CNI** for production
2. **Enable Network Policy** - prefer Azure Network Policy for simplicity
3. **Use Private Endpoints** for API server in production
4. **Implement NSG flow logs** for audit compliance
5. **Restrict egress** using Azure Firewall or UDRs
6. **Regular review** of NSG rules (quarterly)

## Required Forms & Approvals

- **New AKS Cluster:** Form AKS-DEPLOY-001
- **NSG Rule Changes:** Form NET-NSG-CHANGE
- **VNet Peering:** Form NET-PEER-REQ
- **Public IP Assignment:** Form SEC-PUBLIC-IP
- **Security Exception:** Form SEC-EXCEPTION

## Contact & Support

- **Slack Channel:** #cloud-networking
- **Email:** cloud-infra@cvshealth.com
- **On-Call:** PagerDuty - AKS Network Team