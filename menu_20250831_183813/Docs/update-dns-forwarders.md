# Update DNS Forwarders Script

## Overview

The `update_dns_forwarders.py` script is a Python utility designed to remotely manage DNS forwarder configurations in a Podman container. It connects to a remote system via SSH as a regular user (with sudo privileges) and can:

- Replace any IP address with another in the DNS configuration
- Create timestamped backups of configuration files
- Restore configurations from previous backups
- List all available backups
- Revert changes by restoring the most recent backup

The script uses sudo to execute all podman commands, as the container is running as the root user.

## Features

- **Flexible IP Replacement**: Replace any IP address with another (not just 8.8.8.8)
- **Backup Management**: Create timestamped backups and list/restore from them
- **Restore Functionality**: Easily revert changes by restoring from backups
- **Remote SSH Execution**: Connects to remote systems using SSH with support for both password and key-based authentication
- **Automatic Backup**: Creates a timestamped backup of the configuration file before making changes
- **Configuration Verification**: Verifies the changes were applied correctly before restarting the container
- **Container Management**: Automatically restarts the DNS container after configuration changes
- **Error Handling**: Comprehensive error handling and logging throughout the process
- **Dry Run Mode**: Test the connection and backup process without making actual changes

## Prerequisites

### Local System Requirements
- Python 3.6 or higher
- SSH client installed
- Network connectivity to the remote system

### Remote System Requirements
- Podman installed and configured
- A running container named "dns" managed by root-level podman
- SSH access for a regular user with sudo privileges (root SSH typically disabled)
- The user must have passwordless sudo or provide sudo password when prompted
- The container must have `/etc/named.conf` file with DNS forwarder configuration

## Installation

The script is located in the `Python/` directory of the RHCI_Tools repository:

```bash
cd /path/to/RHCI_Tools/Python/
```

Ensure the script is executable:

```bash
chmod +x update_dns_forwarders.py
```

## Usage

### Basic Syntax

```bash
python update_dns_forwarders.py <host> <new_ip> [options]
```

### Required Arguments

- `host`: The hostname or IP address of the remote system
- `new_ip`: The new DNS forwarder IP address (not required when using --restore or --list-backups)

### Optional Arguments

- `-u, --username`: SSH username (default: instructor)
- `-k, --key`: Path to SSH private key file for authentication
- `--from-ip`: IP address to replace (default: 8.8.8.8)
- `--restore`: Restore configuration from most recent backup
- `--restore-from`: Restore from a specific backup file
- `--list-backups`: List all available backup files
- `--dry-run`: Perform backup only without making changes
- `--no-backup`: Skip creating a backup of named.conf
- `-v, --verbose`: Enable verbose output for debugging

### Examples

#### 1. Basic Usage with Password Authentication

Update DNS forwarders on a remote system using the default 'instructor' user (with sudo privileges):

```bash
python update_dns_forwarders.py remote.example.com 192.168.1.1
```

Note: The script will SSH as 'instructor' user by default and use sudo to run podman commands.

#### 2. Using SSH Key Authentication

Update DNS forwarders using an SSH key for authentication:

```bash
python update_dns_forwarders.py remote.example.com 10.0.0.1 -k ~/.ssh/id_rsa
```

#### 3. Specifying a Different Username

Connect as a different user (requires sudo privileges):

```bash
python update_dns_forwarders.py remote.example.com 8.8.4.4 -u admin
```

#### 4. Dry Run Mode

Test the connection and create a backup without making changes:

```bash
python update_dns_forwarders.py remote.example.com 1.1.1.1 --dry-run
```

#### 5. Verbose Mode for Troubleshooting

Enable detailed logging output:

```bash
python update_dns_forwarders.py remote.example.com 172.16.0.1 -v
```

#### 6. Replace Specific IP Address

Replace a specific IP address (not just 8.8.8.8) with another:

```bash
# Replace 192.168.1.1 with 10.0.0.1
python update_dns_forwarders.py remote.example.com 10.0.0.1 --from-ip 192.168.1.1
```

#### 7. Revert Changes (Restore from Backup)

Restore the configuration from the most recent backup:

```bash
python update_dns_forwarders.py remote.example.com --restore
```

#### 8. List Available Backups

View all available backup files:

```bash
python update_dns_forwarders.py remote.example.com --list-backups
```

#### 9. Restore from Specific Backup

Restore from a specific backup file:

```bash
python update_dns_forwarders.py remote.example.com --restore-from /etc/named.conf.backup.20241215_143022
```

#### 10. Revert to Original DNS (8.8.8.8)

If you changed from 8.8.8.8 to another IP and want to change back:

```bash
# Change back to 8.8.8.8 from whatever current IP is set
python update_dns_forwarders.py remote.example.com 8.8.8.8 --from-ip 192.168.1.1
```

#### 11. Skip Backup Creation

Update without creating a backup (not recommended):

```bash
python update_dns_forwarders.py remote.example.com 192.168.100.1 --no-backup
```

## How It Works

### Update Operation

When updating DNS forwarders, the script:

1. **SSH Connection Test**: Validates the SSH connection to the remote host
2. **Container Status Check**: Verifies that the "dns" container is running
3. **Configuration Backup**: Creates a timestamped backup (e.g., `/etc/named.conf.backup.20241215_143022`)
4. **Update Forwarders**: Replaces all occurrences of the specified IP (default: 8.8.8.8) with the new IP
5. **Verification**: Confirms the new IP address is present in the configuration
6. **Container Restart**: Restarts the DNS container to apply changes
7. **Final Verification**: Confirms the container is running after restart

### Restore Operation

When restoring from backup:

1. **SSH Connection Test**: Validates the SSH connection to the remote host
2. **Container Status Check**: Verifies that the "dns" container is running
3. **Backup Selection**: Uses the most recent backup or the specified backup file
4. **Configuration Restore**: Copies the backup file over the current configuration
5. **Container Restart**: Restarts the DNS container to apply the restored configuration
6. **Final Verification**: Confirms the container is running after restart

## Configuration File Format

The script expects the DNS configuration file (`/etc/named.conf`) to contain forwarders in one of these formats:

### Single Line Format
```
forwarders { 8.8.8.8; };
```

### Multi-Line Format
```
forwarders {
    8.8.8.8;
    8.8.4.4;
};
```

The script will replace all occurrences of `8.8.8.8` with the specified IP address.

## Error Handling

The script includes comprehensive error handling for common scenarios:

- **SSH Connection Failures**: Reported with connection details
- **Container Not Running**: Exits with clear error message
- **Permission Denied**: Occurs when sudo privileges are missing
- **Configuration Syntax Errors**: Detected during verification
- **Container Restart Failures**: Reported with podman error details

## Logging

The script uses Python's logging module to provide informative output:

- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues that don't stop execution
- **ERROR**: Critical errors that cause the script to exit
- **DEBUG**: Detailed information (enabled with `-v` flag)

Log messages include timestamps and severity levels:

```
2024-01-15 10:30:45 - INFO - Testing SSH connection to remote.example.com...
2024-01-15 10:30:46 - INFO - SSH connection test successful
2024-01-15 10:30:46 - INFO - Checking if container 'dns' is running...
```

## Security Considerations

1. **SSH Access**: The script connects via SSH as a regular user (not root, as root SSH is typically disabled for security). The user must have sudo privileges.

2. **SSH Keys**: When using SSH key authentication, ensure your private key is properly protected with appropriate file permissions (600)

3. **Sudo Access**: The script requires sudo privileges on the remote system to manage Podman containers running as root. The default 'instructor' user must have sudo privileges. Ideally, configure passwordless sudo for podman commands or be prepared to enter the sudo password.

4. **Backup Files**: Backup files are created within the container at `/etc/named.conf.backup`. Ensure these don't accumulate over time

5. **IP Validation**: The script validates IP address format but doesn't verify network reachability

## Troubleshooting

### Common Issues and Solutions

#### SSH Connection Timeout

**Problem**: The script times out when trying to connect

**Solution**: 
- Verify network connectivity: `ping <host>`
- Check SSH service status on remote host
- Ensure firewall allows SSH (port 22)

#### Permission Denied

**Problem**: Cannot execute podman commands

**Solution**:
- Ensure the SSH user has sudo privileges
- Configure passwordless sudo for podman commands:
  ```bash
  # Add to /etc/sudoers.d/podman (on remote system)
  instructor ALL=(root) NOPASSWD: /usr/bin/podman
  ```
- Alternatively, ensure you can provide the sudo password when prompted
- Verify the user is in the appropriate groups (wheel/sudo)

#### Container Not Found

**Problem**: The "dns" container is not running

**Solution**:
- List running containers: `sudo podman ps`
- Start the container if stopped: `sudo podman start dns`
- Verify container name is exactly "dns"

#### Configuration Not Updated

**Problem**: The IP address wasn't replaced in the configuration

**Solution**:
- Check the format of the forwarders line in `/etc/named.conf`
- Verify 8.8.8.8 exists in the configuration
- Use verbose mode (`-v`) to see detailed sed command output

#### Container Fails to Restart

**Problem**: The container doesn't start after configuration change

**Solution**:
- Check container logs: `sudo podman logs dns`
- Verify configuration syntax is valid
- Restore from backup: `sudo podman exec dns cp /etc/named.conf.backup /etc/named.conf`

### Debug Mode

For detailed troubleshooting, run the script with verbose output:

```bash
python update_dns_forwarders.py remote.example.com 192.168.1.1 -v 2>&1 | tee debug.log
```

This will:
- Enable debug-level logging
- Save all output to `debug.log` for analysis
- Display output on screen in real-time

## Best Practices

### General Practices
1. **Always Create Backups**: Don't use `--no-backup` unless absolutely necessary
2. **Test in Non-Production**: Use dry-run mode to test before applying changes
3. **Verify DNS Resolution**: After updating, test DNS resolution from clients
4. **Document Changes**: Keep a log of when and why forwarders were changed
5. **Monitor Container Health**: Check container logs after restart for any errors

### Backup Management
1. **Regular Cleanup**: Periodically clean up old backup files to prevent disk space issues
2. **List Before Restore**: Always use `--list-backups` to see available backups before restoring
3. **Timestamped Backups**: The script creates timestamped backups automatically for easy tracking
4. **Test Restore Process**: Periodically test the restore process in non-production environments

### Reverting Changes
1. **Quick Revert**: Use `--restore` to quickly revert to the previous configuration
2. **Specific Restore**: Use `--restore-from` when you need to restore a specific configuration
3. **Manual Revert**: You can also manually change IPs back using `--from-ip` parameter

## Integration with Automation

The script can be integrated into larger automation workflows:

### Ansible Playbook Example

```yaml
- name: Update DNS forwarders on multiple hosts
  hosts: dns_servers
  tasks:
    - name: Copy update script
      copy:
        src: update_dns_forwarders.py
        dest: /tmp/update_dns_forwarders.py
        mode: '0755'
    
    - name: Update forwarders
      command: python /tmp/update_dns_forwarders.py localhost {{ new_dns_ip }}
      delegate_to: localhost
```

### Shell Script Wrapper

```bash
#!/bin/bash
# Update DNS forwarders on multiple hosts

HOSTS="dns1.example.com dns2.example.com dns3.example.com"
NEW_IP="192.168.1.1"

for host in $HOSTS; do
    echo "Updating $host..."
    python update_dns_forwarders.py "$host" "$NEW_IP" -k ~/.ssh/id_rsa
    if [ $? -eq 0 ]; then
        echo "✅ $host updated successfully"
    else
        echo "❌ Failed to update $host"
    fi
done
```

## Return Codes

The script uses standard exit codes:

- `0`: Success - All operations completed successfully
- `1`: Failure - An error occurred during execution

Check the return code in scripts:

```bash
python update_dns_forwarders.py remote.example.com 192.168.1.1
if [ $? -eq 0 ]; then
    echo "Update successful"
else
    echo "Update failed"
fi
```

## Limitations

1. **Container Name**: The script expects the container to be named exactly "dns"
2. **Configuration Format**: Only replaces 8.8.8.8; other forwarders remain unchanged
3. **Single Container**: Updates only one container at a time
4. **Root Podman**: Designed for containers managed by root-level Podman (accessed via sudo)
5. **SSH Requirements**: Requires SSH as a regular user with sudo privileges (does not support direct root SSH)

## Future Enhancements

Potential improvements for future versions:

- Support for multiple container names via configuration
- Ability to update multiple forwarder IPs
- Configuration file templates
- Rollback functionality
- Health checks after restart
- Support for rootless Podman containers

## Support

For issues, questions, or contributions related to this script, please refer to the main RHCI_Tools repository documentation or contact the development team.

## License

This script is part of the RHCI_Tools suite and follows the same licensing terms as the parent project.
