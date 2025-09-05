# Lab CloudInit VMs Extraction Tool

## Overview

`Lab_CloudInit_VMs.py` is a Python utility that dynamically extracts VM names from ICMF manifest files based on the course configuration in `/etc/rht`. Unlike the static `extract_vm_names.py` script, this tool automatically determines which manifest to use based on the `RHT_COURSE` value.

## Features

- **Dynamic Manifest Selection**: Automatically reads the `RHT_COURSE` value from `/etc/rht` and finds the corresponding manifest in `/content/manifests`
- **Flexible Override Options**: Allows manual specification of course code or manifest file
- **Multiple Output Formats**: Supports text, YAML, and JSON output formats
- **Verbose Mode**: Provides detailed information about the extraction process
- **Results Saving**: Can save extracted data to a YAML file for later use

## Prerequisites

- Python 3.6 or higher
- Access to `/etc/rht` file (for automatic course detection)
- ICMF manifest files in `/content/manifests` directory

## Installation

The script is located in the `Python/` directory of the RHCI_Tools repository:

```bash
cd /home/kiosk/RHCI_Tools/Python
chmod +x Lab_CloudInit_VMs.py
```

## Usage

### Basic Usage (Automatic Detection)

The simplest way to use the tool is to run it without any arguments. It will:
1. Read the `RHT_COURSE` value from `/etc/rht`
2. Find the matching manifest in `/content/manifests`
3. Extract and display VM names

```bash
./Lab_CloudInit_VMs.py
```

### Command-Line Options

```
Options:
  -h, --help                          Show help message
  --course COURSE, -c COURSE          Override course code (default: read from /etc/rht)
  --manifest MANIFEST, -m MANIFEST    Explicit manifest file path (overrides auto-detection)
  --manifests-dir DIR, -d DIR         Directory containing manifest files (default: /content/manifests)
  --save-results                      Save results to lab_cloudinit_vms.yml
  --output-format {text,yaml,json}    Output format (default: text)
  --verbose, -v                        Enable verbose output
```

### Examples

#### Display VM names with verbose output
```bash
./Lab_CloudInit_VMs.py --verbose
```

#### Use a specific course code
```bash
./Lab_CloudInit_VMs.py --course RHCIfoundation
```

#### Use a specific manifest file directly
```bash
./Lab_CloudInit_VMs.py --manifest /path/to/custom.icmf
```

#### Output in JSON format
```bash
./Lab_CloudInit_VMs.py --output-format json
```

#### Save results to a YAML file
```bash
./Lab_CloudInit_VMs.py --save-results
```

#### Look for manifests in a custom directory
```bash
./Lab_CloudInit_VMs.py --manifests-dir /custom/manifests/path
```

## Output Formats

### Text Format (Default)
```
Course: lb0000
Manifest: LB0000-RHEL10.0-1.r2025080813-ILT+RAV-8-en_US.icmf
Curriculum: LB0000
Found 3 cidata ISOs

Extracted 3 VM names:
  - classroom
  - utility
  - workstation
```

### JSON Format
```json
{
  "curriculum_name": "LB0000",
  "manifest_file": "LB0000-RHEL10.0-1.r2025080813-ILT+RAV-8-en_US.icmf",
  "cidata_isos": [
    "lb0000-classroom-cidata-20250722.iso",
    "lb0000-utility-cidata-20250715.iso",
    "lb0000-workstation-cidata-20250808.iso"
  ],
  "vm_names": [
    "classroom",
    "utility",
    "workstation"
  ],
  "course_code": "lb0000"
}
```

### YAML Format
```yaml
course_code: lb0000
manifest_file: LB0000-RHEL10.0-1.r2025080813-ILT+RAV-8-en_US.icmf
curriculum_name: LB0000
cidata_isos:
  - lb0000-classroom-cidata-20250722.iso
  - lb0000-utility-cidata-20250715.iso
  - lb0000-workstation-cidata-20250808.iso
vm_names:
  - classroom
  - utility
  - workstation
```

## How It Works

1. **Course Detection**: The script reads `/etc/rht` to find the `RHT_COURSE` value
2. **Manifest Discovery**: Searches `/content/manifests` for a manifest file matching the course code pattern
3. **VM Extraction**: Parses the ICMF manifest to find cidata ISO filenames
4. **Name Parsing**: Extracts VM names from the cidata ISO filename pattern: `{course}-{vm_name}-cidata-{date}.iso`

## Manifest Selection Logic

The script uses the following logic to find the appropriate manifest:

1. Looks for files matching `{COURSE_CODE}-*.icmf` (trying uppercase, lowercase, and original case)
2. If multiple manifests are found for the same course, uses the most recent one (alphabetically sorted)
3. Performs case-insensitive matching as a fallback

## Error Handling

The script handles several error conditions:

- Missing `/etc/rht` file
- Missing or empty `RHT_COURSE` value
- Missing `/content/manifests` directory
- No matching manifest file for the course
- Invalid ICMF file format

When errors occur, the script provides clear error messages and exits with a non-zero status code.

## Integration with Other Tools

This tool can be integrated with other RHCI tools and scripts:

### Using with Ansible
```yaml
- name: Extract VM names for current course
  command: /home/kiosk/RHCI_Tools/Python/Lab_CloudInit_VMs.py --output-format json
  register: vm_info

- name: Use extracted VM names
  debug:
    msg: "Found VMs: {{ (vm_info.stdout | from_json).vm_names }}"
```

### Using in Shell Scripts
```bash
#!/bin/bash
# Extract VM names and save to file
/home/kiosk/RHCI_Tools/Python/Lab_CloudInit_VMs.py --save-results

# Read the results
if [ -f lab_cloudinit_vms.yml ]; then
    echo "VM extraction completed successfully"
    cat lab_cloudinit_vms.yml
fi
```

## Comparison with extract_vm_names.py

| Feature | extract_vm_names.py | Lab_CloudInit_VMs.py |
|---------|---------------------|---------------------|
| Manifest Selection | Hard-coded filename | Dynamic based on RHT_COURSE |
| Course Detection | Not supported | Reads from /etc/rht |
| Override Options | Only manifest file | Course code and manifest file |
| Auto-discovery | No | Yes |
| Output File | vm_names_extracted.yml | lab_cloudinit_vms.yml |

## Troubleshooting

### Issue: "File /etc/rht not found"
**Solution**: Use the `--course` option to specify the course code manually, or use `--manifest` to specify the manifest file directly.

### Issue: "No manifest file found for course"
**Solution**: 
- Verify the course code is correct
- Check that manifest files exist in `/content/manifests`
- Use `--manifests-dir` to specify an alternative directory
- Use `--manifest` to specify the exact manifest file

### Issue: "Multiple manifests found"
**Solution**: The script will automatically use the most recent manifest (based on filename). To use a specific one, provide the full path with `--manifest`.

## Container Usage

When using this tool in a containerized environment with Podman:

```bash
# Mount necessary directories
podman run -v /etc/rht:/etc/rht:ro \
           -v /content/manifests:/content/manifests:ro \
           rhci-tools \
           python3 /app/Python/Lab_CloudInit_VMs.py
```

## License

This tool is part of the RHCI_Tools suite and follows the same licensing terms.
