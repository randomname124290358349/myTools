# Complete Tutorial: Creating Command Definitions for `commands.json`

## Objective

This comprehensive guide explains how to create command definitions for network utilities and system commands that automatically adapt to the operating system where the application is running. You'll learn both basic command structure and advanced platform-specific features, including commands exclusive to certain platforms.

## 1. High-Level Structure

The `commands.json` file is a single JSON object where each key is a unique, machine-friendly identifier for a command (e.g., `"ping"`, `"nslookup"`). The value associated with each key is a **Command Definition Object**.

```json
{
  "command_identifier_1": { ... Command Definition Object 1 ... },
  "command_identifier_2": { ... Command Definition Object 2 ... }
}
```

## 2. Platform Adaptation Features

### Automatic Command Filtering
- **Backend**: Automatically filters commands based on operating system
- **Frontend**: Shows only commands compatible with current platform
- **Detection**: Automatically identifies Windows vs Unix/Linux

### Platform Specification Levels

#### A. Command-Specific (Top Level)
Commands that exist only on a specific platform:

```json
"ipconfig": {
  "name": "IP Configuration", 
  "description": "Display and configure IP settings (Windows only)",
  "platforms": ["windows"],
  "windows": { ... },
  "options": [ ... ]
}
```

#### B. Option-Specific (Option Level)
Options that exist only on certain platforms:

```json
{
  "id": "flood",
  "label": "Flood",
  "type": "checkbox",
  "platforms": ["unix"]
}
```

## 3. Complete Command Definition Object Structure

Each command is defined by an object with the following top-level keys:

| Key           | Type           | Required | Description                                                                                                                              |
|---------------|----------------|----------|------------------------------------------------------------------------------------------------------------------------------------------|
| `name`        | String         | Yes      | Human-readable command name (e.g., "Ping", "Traceroute")                                                                                |
| `description` | String         | Yes      | Brief, user-friendly description of the command's purpose                                                                               |
| `target`      | String or Null | Yes      | ID of option that serves as main target (e.g., hostname or IP). Use `null` if no target exists (like `netstat`)                      |
| `platforms`   | Array          | Optional | Array of supported platforms: `["windows"]`, `["unix"]`, or `["windows", "unix"]`. If omitted, assumes support for both             |
| `windows`     | Object         | Yes*     | Windows-specific configuration (*required if supporting Windows)                                                                         |
| `unix`        | Object         | Yes*     | Unix-specific configuration (*required if supporting Unix/Linux)                                                                        |
| `options`     | Array          | Yes      | Array of option objects defining user-configurable parameters                                                                           |

## 4. Platform-Specific Definitions (`windows` and `unix`)

These objects define how to construct the command string for each operating system. They share the same structure:

| Key    | Type   | Required | Description                                                                                                                                                                                                   |
|--------|--------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `base` | String | Yes      | The base executable name for the command (e.g., `"ping"`, `"traceroute"`)                                                                                                                                    |
| `flags`| Object | Yes      | A key-value map where each key is the `id` of an **Option Object**, and the value is an array of strings representing the corresponding command-line flag(s)                                               |

### 4.1. Flags Mapping Logic

The `flags` object is critical. It connects a user's input (defined in `options`) to the actual command-line arguments.

*   **For options requiring a value** (e.g., `type: "number"` or `type: "text"`): The array contains the flag that precedes the value.
    *   Example: `"count": ["-c"]` (Unix) means if the user enters `5` for the `count` option, the command will include `-c 5`.
*   **For boolean options** (e.g., `type: "checkbox"`): The array contains the flag that is simply present or absent.
    *   Example: `"quiet": ["-q"]` (Unix) means if the `quiet` checkbox is checked, the command will include `-q`.
*   **For complex/multi-part flags**: The array can contain multiple strings. This is common on Windows.
    *   Example: `"tcp": ["-p", "tcp"]` (Windows `netstat`) means if the `tcp` checkbox is checked, the command will include the full sequence `-p tcp`.

## 5. The `options` Array

This is the core of the command definition, as it drives the UI and parameter validation. It is an array of **Option Objects**. Each object defines one parameter.

### 5.1. Option Object Schema

| Key           | Type    | Description                                                                                                                                           |
|---------------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `id`          | String  | A unique, machine-friendly identifier for the option. **This must match a key in the `flags` objects.**                                               |
| `label`       | String  | The human-readable label for the UI form field                                                                                                        |
| `type`        | String  | The type of UI input. Supported values: `"text"`, `"number"`, `"checkbox"`, `"select"`                                                               |
| `required`    | Boolean | (Optional) If `true`, a value must be provided for this option. Defaults to `false`                                                                  |
| `placeholder` | String  | (Optional) Placeholder text for input fields (`text`, `number`)                                                                                      |
| `value`       | String  | (Optional) A default value for the input. For `checkbox`, any non-empty value implies it's checked by default                                       |
| `min` / `max` | Number  | (Optional) For `type: "number"`, specifies the minimum and maximum allowed values                                                                    |
| `platforms`   | Array   | (Optional) An array of strings (`"windows"`, `"unix"`). If present, this option is **only** available on the specified platforms                    |
| `options`     | Array   | (Required for `type: "select"`) An array of objects, each with a `value` (string to be used) and a `text` (string displayed in UI)                |

## 6. Step-by-Step Guide: Creating a Basic Command

Let's create a definition for the `arp` command as an example. Its basic usage is to display the ARP table (`arp -a`).

**Step 1: Choose an Identifier and Basic Info**
The identifier will be `"arp"`. The name is "ARP Table" and the description is "Displays and modifies the IP-to-Physical address translation tables."

**Step 2: Identify the Target**
The basic `arp -a` command has no target, so we set `target: null`.

**Step 3: Define Platform-Specific Base Commands**
The base command is `"arp"` on both Windows and Unix.

**Step 4: Define the `options`**
Create an option for displaying the table with the `-a` flag:
- `id`: `"display_all"`
- `label`: `"Display all entries"`
- `type`: `"checkbox"`
- `value`: `"true"` (checked by default)

**Step 5: Map Options to `flags`**
Connect the `"display_all"` option to `-a` on both platforms.

**Step 6: Complete Definition**
```json
"arp": {
  "name": "ARP Table",
  "description": "Displays and modifies the IP-to-Physical address translation tables.",
  "target": null,
  "windows": {
    "base": "arp",
    "flags": {
      "display_all": ["-a"]
    }
  },
  "unix": {
    "base": "arp",
    "flags": {
      "display_all": ["-a"]
    }
  },
  "options": [
    {
      "id": "display_all",
      "label": "Display all entries",
      "type": "checkbox",
      "value": "true"
    }
  ]
}
```

## 7. Advanced Platform-Specific Examples

### 7.1. Windows-Exclusive Command

```json
"sfc": {
  "name": "System File Checker",
  "description": "Scans and repairs system files (Windows only)",
  "target": null,
  "platforms": ["windows"],
  "windows": {
    "base": "sfc",
    "flags": {
      "scannow": ["/scannow"],
      "scanfile": ["/scanfile"],
      "verifyonly": ["/verifyonly"]
    }
  },
  "options": [
    {
      "id": "scannow",
      "label": "Scan all system files",
      "type": "checkbox"
    },
    {
      "id": "scanfile",
      "label": "Scan specific file",
      "type": "text",
      "placeholder": "C:\\Windows\\System32\\file.dll"
    },
    {
      "id": "verifyonly",
      "label": "Verify only (don't repair)",
      "type": "checkbox"
    }
  ]
}
```

### 7.2. Linux/Unix-Exclusive Command

```json
"ps": {
  "name": "Process Status",
  "description": "Display running processes (Unix only)",
  "target": null,
  "platforms": ["unix"],
  "unix": {
    "base": "ps",
    "flags": {
      "all": ["-A"],
      "full": ["-f"],
      "user": ["-u"],
      "forest": ["-F"]
    }
  },
  "options": [
    {
      "id": "all",
      "label": "Show all processes",
      "type": "checkbox"
    },
    {
      "id": "full",
      "label": "Full format",
      "type": "checkbox"
    },
    {
      "id": "user",
      "label": "Show by user",
      "type": "text",
      "placeholder": "username"
    },
    {
      "id": "forest",
      "label": "Forest view",
      "type": "checkbox"
    }
  ]
}
```

### 7.3. Cross-Platform Command with Platform-Specific Options

```json
"find_files": {
  "name": "Find Files",
  "description": "Search for files and directories",
  "target": "path",
  "windows": {
    "base": "dir",
    "flags": {
      "path": [],
      "recursive": ["/S"],
      "pattern": []
    }
  },
  "unix": {
    "base": "find",
    "flags": {
      "path": [],
      "name": ["-name"],
      "type": ["-type", "f"],
      "executable": ["-executable"]
    }
  },
  "options": [
    {
      "id": "path",
      "label": "Search Path",
      "type": "text",
      "placeholder": "C:\\ or /home/user",
      "required": true
    },
    {
      "id": "pattern",
      "label": "File Pattern",
      "type": "text",
      "placeholder": "*.txt",
      "platforms": ["windows"]
    },
    {
      "id": "name",
      "label": "File Name",
      "type": "text",
      "placeholder": "filename.txt",
      "platforms": ["unix"]
    },
    {
      "id": "recursive",
      "label": "Search Subdirectories",
      "type": "checkbox",
      "platforms": ["windows"]
    },
    {
      "id": "type",
      "label": "Files only",
      "type": "checkbox",
      "platforms": ["unix"]
    },
    {
      "id": "executable",
      "label": "Executable files only",
      "type": "checkbox",
      "platforms": ["unix"]
    }
  ]
}
```

### 7.4. Complete Cross-Platform Network Command Example

```json
"ping": {
  "name": "Ping",
  "description": "Send ICMP echo requests to network hosts",
  "target": "host",
  "windows": {
    "base": "ping",
    "flags": {
      "host": [],
      "count": ["-n"],
      "size": ["-l"],
      "timeout": ["-w"],
      "continuous": ["-t"]
    }
  },
  "unix": {
    "base": "ping",
    "flags": {
      "host": [],
      "count": ["-c"],
      "size": ["-s"],
      "timeout": ["-W"],
      "flood": ["-f"]
    }
  },
  "options": [
    {
      "id": "host",
      "label": "Host",
      "type": "text",
      "placeholder": "google.com or 8.8.8.8",
      "required": true
    },
    {
      "id": "count",
      "label": "Number of pings",
      "type": "number",
      "placeholder": "4",
      "min": 1,
      "max": 100
    },
    {
      "id": "size",
      "label": "Packet size (bytes)",
      "type": "number",
      "placeholder": "32",
      "min": 1,
      "max": 65500
    },
    {
      "id": "timeout",
      "label": "Timeout (ms)",
      "type": "number",
      "placeholder": "1000",
      "min": 1,
      "max": 10000
    },
    {
      "id": "continuous",
      "label": "Continuous ping",
      "type": "checkbox",
      "platforms": ["windows"]
    },
    {
      "id": "flood",
      "label": "Flood ping",
      "type": "checkbox",
      "platforms": ["unix"]
    }
  ]
}
```

## Filtering Flow

### Backend (`app.py`)
1. **Detection**: `platform.system().lower()` detects the OS
2. **Command Filtering**: Removes unsupported commands
3. **Option Filtering**: Removes options specific to other platforms  
4. **Validation**: Checks if configuration exists for current platform

### Frontend (`index.html`)
1. **Receives**: Only pre-filtered commands from backend
2. **Displays**: Badge showing detected platform
3. **Adapts**: Interface based on available commands
4. **Fallback**: Additional client-side verification

## 8. Comprehensive Best Practices

### 8.1. Consistency and Structure
- **Use clear and consistent `id` values**: The `id` is the glue between `options` and `flags`
- **Define `options` first**: List all parameters a command can take in the `options` array, then fill in the `flags` mappings for each platform
- **Validate JSON**: Ensure your final output is valid JSON. A single misplaced comma can invalidate the entire file

### 8.2. Platform-Specific Guidelines
- **Consistent naming**: Use descriptive names that indicate platform when appropriate
  - Ex: "IP Configuration (Windows)" vs "Interface Configuration (Unix)"
- **Informative descriptions**: Include "(Windows only)" or "(Unix only)" in description when appropriate
- **Pay attention to flag differences**: Windows often uses `/` while Unix uses `-`. Handle multi-part flags correctly
  - Example: Windows `netstat -p tcp` vs Unix `netstat -t`

### 8.3. Cross-Platform Considerations
- **Test on multiple platforms**: Test commands on Windows, Linux, and macOS when possible
- **Handle equivalent functionality differently**: `ping -t` (Windows continuous) vs no count limit (Unix)
- **Use platform-specific options**: Leverage the `platforms` key in options for platform-exclusive features

### 8.4. User Experience
- **Provide helpful defaults**: Use `value` for common default selections
- **Clear placeholders**: Provide meaningful placeholder text that shows expected formats
- **Appropriate input types**: Use `number` with `min`/`max` for numeric inputs, `select` for predefined choices
- **Required field validation**: Mark essential options as `required: true`

### 8.5. Advanced Features
- **Graceful fallbacks**: Always validate that platform configuration exists
- **Clear error messages**: Provide informative error messages for unsupported commands
- **Documentation**: Document differences between platforms and include usage examples

## Debugging

### Check Detected Platform
Access `/api/platform` to see platform information:

```json
{
  "os": "windows",
  "platform": "windows", 
  "system": "Windows",
  "machine": "AMD64",
  "version": "10.0.19041"
}
```

### Check Filtered Commands
Access `/api/commands` to see only commands available on current platform.

## Pre-configured Example Commands

The application includes comprehensive examples of different command types:

### Cross-Platform Commands
- **`ping`**: ICMP echo requests with platform-specific options (continuous vs flood)
- **`nslookup`**: DNS lookups with different query types
- **`tracert`/`traceroute`**: Network path tracing (different base commands per platform)
- **`netstat`**: Network statistics with platform-specific flag formats
- **`arp`**: ARP table display and management

### Platform-Exclusive Commands
- **Windows Only**: 
  - `ipconfig`: IP configuration display and management
  - `sfc`: System File Checker for integrity verification
- **Unix Only**: 
  - `ifconfig`: Network interface configuration
  - `ps`: Process status with Unix-specific formatting options

### Command Categories by Complexity
1. **Basic**: Single-purpose commands with minimal options (`arp`, basic `ping`)
2. **Intermediate**: Commands with multiple boolean and text options (`nslookup`, `netstat`)
3. **Advanced**: Cross-platform commands with platform-specific options and complex flag mapping (`ping` with all features, `find_files`)

These examples serve as templates for creating new command definitions and demonstrate all the features covered in this tutorial.
