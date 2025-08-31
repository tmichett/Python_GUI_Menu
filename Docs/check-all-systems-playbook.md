# Check All Systems Playbook

## Overview
The `Check_All_Systems.yml` playbook performs system verification checks across all hosts in the Ansible inventory, excluding Foundation and Instructor groups.

## Checks Performed

### 1. SSH Connectivity Check
- **Target Hosts**: all, !Foundation, !Instructor
- **Purpose**: Verifies that Ansible can connect to all target hosts
- **Module**: `ansible.builtin.ping`
- **Tags**: connectivity

### 2. MTU Verification
- **Target Hosts**: all, !Foundation, !Instructor  
- **Purpose**: Ensures ethernet network interfaces have the correct MTU setting
- **Checks**: MTU value is 1500
- **Interfaces Checked**: Only interfaces starting with "e" (e.g., eth0, ens33, enp0s3)
- **Interfaces Ignored**: 
  - Loopback (lo)
  - Container interfaces (podman*, docker*)
  - Virtual bridges (virbr*)
  - Tunnel interfaces (tun*)
  - Any other non-ethernet interfaces
- **Tags**: mtu

## Usage

### Run All Checks
```bash
ansible-playbook Playbooks/Check_All_Systems.yml
```

### Run Specific Checks Using Tags

Check only connectivity:
```bash
ansible-playbook Playbooks/Check_All_Systems.yml --tags connectivity
```

Check only MTU settings:
```bash
ansible-playbook Playbooks/Check_All_Systems.yml --tags mtu
```

### Limit to Specific Hosts
```bash
ansible-playbook Playbooks/Check_All_Systems.yml --limit workstation
```

## Requirements
- Ansible installed
- Ansible inventory configured at `/etc/ansible/inventory`
- SSH access to target hosts

## Error Messages

### Connectivity Issues
If a host is unreachable, you'll see a failure in the SSH connectivity check task.

### MTU Issues
If an ethernet interface has an incorrect MTU, you'll see:
```
Fix the MTU for the {interface} port on {hostname}.
The MTU should be 1500, but was found to be {actual_mtu}.
```

## Excluded Hosts
The playbook excludes the following groups:
- **Foundation**: Foundation systems (typically the control node)
- **Instructor**: Instructor systems

## Interface Naming Conventions
The playbook checks interfaces starting with "e" which covers:
- **eth#**: Traditional ethernet naming (eth0, eth1)
- **ens#**: Systemd predictable naming for embedded interfaces
- **enp#s#**: Systemd predictable naming for PCI interfaces
- **eno#**: Systemd predictable naming for onboard interfaces

## Troubleshooting

### Common Issues

1. **"Unexpected Exception: 'startswith'"**
   - Ensure you're using a recent version of Ansible that supports the `startswith()` method
   - Alternative: Use regex pattern matching if needed

2. **MTU check fails on valid interfaces**
   - Verify the interface actually starts with "e"
   - Check actual MTU: `ip link show <interface>`
   - Manually set MTU if needed: `sudo ip link set dev <interface> mtu 1500`

3. **Playbook skips all interfaces**
   - List interfaces: `ansible <host> -m setup -a "filter=ansible_interfaces"`
   - Verify interface naming on target systems

## Integration with RHCI Tools
This playbook is part of the RHCI Tools suite and can be used:
- As a pre-flight check before lab exercises
- For periodic system health verification
- As part of automated testing workflows
