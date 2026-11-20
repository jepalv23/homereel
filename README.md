# promax-setup
# Homelab Infrastructure

A production-style personal infrastructure lab built around a single high-performance virtualization host.

The lab is used to experiment with virtualization, containerization, networking, observability, automation, backups, and self-hosted services while keeping the environment reproducible and documented.

## Hardware

| Component | Specification |
|---|---|
| CPU | AMD Ryzen 9 7900 — 12 cores / 24 threads |
| Memory | 128 GB DDR5 ECC |
| Boot / OS storage | 1 TB NVMe SSD |
| VM / container storage | 2 × 2 TB NVMe SSDs |
| Network | 10 GbE |
| WAN | Dedicated public IP |
| Hypervisor | Proxmox VE |

### Design goals

1. Keep the hypervisor boring and stable.
2. Isolate workloads with VLANs and firewall policy.
3. Prefer infrastructure-as-code and declarative configuration.
4. Treat backups as part of the system, not an afterthought.
5. Make services disposable: a failed VM should be replaceable from documentation and configuration.
6. Document failures and operational decisions.

## Architecture

```text
                         Internet
                            |
                     Dedicated Public IP
                            |
                    ISP / Edge Firewall
                            |
                         10 GbE
                            |
                 +----------------------+
                 | Proxmox VE Host      |
                 | Ryzen 9 7900         |
                 | 128 GB ECC RAM       |
                 +----------+-----------+
                            |
                    Linux Bridge / VLANs
                            |
        +-------------------+-------------------+
        |                   |                   |
     VLAN 10             VLAN 20             VLAN 30
   Management            Servers              DMZ
        |                   |                   |
   Proxmox UI          VMs / LXCs          Public-facing
   SSH / monitoring    Docker workloads     reverse proxy
```

## Virtualization Plan

The host is intentionally over-provisioned so workloads can be created, destroyed, and tested without constantly redesigning the platform.

| Guest | Type | vCPU | RAM | Purpose |
|---|---|---:|---:|---|
| `pve-mgmt` | VM | 2 | 4 GB | Management utilities |
| `docker-01` | VM | 6 | 16 GB | Container workloads |
| `monitoring-01` | VM | 4 | 12 GB | Prometheus / Grafana |
| `dns-01` | LXC | 2 | 1 GB | DNS / network services |
| `proxy-01` | VM | 2 | 4 GB | Reverse proxy |
| `dev-01` | VM | 4 | 8 GB | Development sandbox |
| `k3s-01` | VM | 4 | 8 GB | Kubernetes experiments |

> Resource assignments are a starting point rather than a claim that every workload must run simultaneously.

## Storage

The three NVMe devices have distinct responsibilities:

```text
1 TB NVMe
└── Proxmox VE
    ├── Host OS
    └── ISO / templates

2 TB NVMe #1
└── VM / LXC storage
    ├── Production workloads
    └── Application data

2 TB NVMe #2
└── VM / LXC storage
    ├── Lab workloads
    └── Snapshots / temporary datasets
```

Important: local NVMe storage is not considered a backup. Backups should ultimately live on separate physical storage or another system.

## Networking

Initial VLAN plan:

| VLAN | Name | CIDR | Purpose |
|---:|---|---|---|
| 10 | Management | `10.10.10.0/24` | Hypervisor and infrastructure management |
| 20 | Servers | `10.10.20.0/24` | Internal services |
| 30 | DMZ | `10.10.30.0/24` | Internet-facing services |
| 40 | Clients | `10.10.40.0/24` | Trusted devices |
| 50 | IoT | `10.10.50.0/24` | Untrusted smart devices |
| 60 | Lab | `10.10.60.0/24` | Experiments and intentionally broken workloads |

The dedicated public IP should terminate at the edge firewall/router rather than being assigned directly to random internal guests.

## Repository Layout

```text
home-lab/
├── ansible/
│   ├── inventories/
│   ├── playbooks/
│   └── roles/
├── diagrams/
├── docs/
│   ├── architecture.md
│   ├── networking.md
│   ├── storage.md
│   ├── backup-strategy.md
│   └── operations.md
├── infrastructure/
│   ├── proxmox/
│   └── terraform/
├── services/
│   ├── docker/
│   ├── monitoring/
│   ├── networking/
│   └── reverse-proxy/
├── scripts/
│   ├── backup/
│   ├── maintenance/
│   └── health-checks/
├── .env.example
├── .gitignore
└── README.md
```

## Operational Principles

- No credentials in Git.
- Management interfaces are never exposed directly to the Internet.
- Public services live in the DMZ.
- Backups are tested by restoring them.
- Configuration changes are documented.
- Monitoring should detect failures before a user notices them.
- Lab workloads are isolated from important services.

## Roadmap

- [x] Install Proxmox VE
- [x] Establish storage layout
- [x] Define VLAN architecture
- [ ] Build management VM
- [ ] Deploy monitoring
- [ ] Deploy centralized logging
- [ ] Configure automated backups
- [ ] Add Ansible provisioning
- [ ] Add Terraform/Proxmox definitions
- [ ] Create public-service DMZ
- [ ] Document disaster recovery
- [ ] Add alerting and uptime checks
