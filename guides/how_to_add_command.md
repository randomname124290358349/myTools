## Tutorial: Creating Command Definitions for `commands.json`

### Objective

This document provides a comprehensive guide for AI agents on how to define new network utility commands for the `commands.json` schema. The goal is to create a structured, platform-aware definition that can be used to dynamically generate a user interface and construct valid shell commands for both Windows and Unix-like operating systems.

### 1. High-Level Structure

The `commands.json` file is a single JSON object. Each key in this object is a unique, machine-friendly identifier for a command (e.g., `"ping"`, `"nslookup"`). The value associated with each key is a **Command Definition Object**.

```json
{
  "command_identifier_1": { ... Command Definition Object 1 ... },
  "command_identifier_2": { ... Command Definition Object 2 ... }
}
```

### 2. The Command Definition Object

Each command is defined by an object with the following top-level keys:

| Key           | Type           | Required | Description                                                                                                                              |
|---------------|----------------|----------|------------------------------------------------------------------------------------------------------------------------------------------|
| `name`        | String         | Yes      | The human-readable name of the command (e.g., "Ping", "Traceroute").                                                                     |
| `description` | String         | Yes      | A brief, user-friendly description of the command's purpose.                                                                             |
| `target`      | String or Null | Yes      | The `id` of the option that serves as the main target of the command (e.g., a hostname or IP). If no target exists (like `netstat`), use `null`. |
| `windows`     | Object         | Yes      | An object containing the command's implementation details for the Windows platform.                                                      |
| `unix`        | Object         | Yes      | An object containing the command's implementation details for Unix-like platforms (Linux, macOS).                                        |
| `options`     | Array          | Yes      | An array of **Option Objects** that define the user-configurable parameters for the command.                                             |

### 3. Platform-Specific Definitions (`windows` and `unix`)

These objects define how to construct the command string for each operating system. They share the same structure:

| Key    | Type   | Required | Description                                                                                                                                                                                                   |
|--------|--------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `base` | String | Yes      | The base executable name for the command (e.g., `"ping"`, `"traceroute"`).                                                                                                                                    |
| `flags`| Object | Yes      | A key-value map where each key is the `id` of an **Option Object**, and the value is an array of strings representing the corresponding command-line flag(s). See the **Flags Mapping Logic** section below. |

#### 3.1. Flags Mapping Logic

The `flags` object is critical. It connects a user's input (defined in `options`) to the actual command-line arguments.

*   **For options requiring a value** (e.g., `type: "number"` or `type: "text"`): The array contains the flag that precedes the value.
    *   Example: `"count": ["-c"]` (Unix) means if the user enters `5` for the `count` option, the command will include `-c 5`.
*   **For boolean options** (e.g., `type: "checkbox"`): The array contains the flag that is simply present or absent.
    *   Example: `"quiet": ["-q"]` (Unix) means if the `quiet` checkbox is checked, the command will include `-q`.
*   **For complex/multi-part flags**: The array can contain multiple strings. This is common on Windows.
    *   Example: `"tcp": ["-p", "tcp"]` (Windows `netstat`) means if the `tcp` checkbox is checked, the command will include the full, static sequence `-p tcp`.

### 4. The `options` Array

This is the core of the command definition, as it drives the UI and parameter validation. It is an array of **Option Objects**. Each object defines one parameter.

#### 4.1. Option Object Schema

| Key           | Type    | Description                                                                                                                                           |
|---------------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `id`          | String  | A unique, machine-friendly identifier for the option. **This must match a key in the `flags` objects.**                                               |
| `label`       | String  | The human-readable label for the UI form field.                                                                                                       |
| `type`        | String  | The type of UI input. Supported values: `"text"`, `"number"`, `"checkbox"`, `"select"`.                                                                 |
| `required`    | Boolean | (Optional) If `true`, a value must be provided for this option. Defaults to `false`.                                                                    |
| `placeholder` | String  | (Optional) Placeholder text for input fields (`text`, `number`).                                                                                      |
| `value`       | String  | (Optional) A default value for the input. For `checkbox`, any non-empty value implies it's checked by default.                                      |
| `min` / `max` | Number  | (Optional) For `type: "number"`, specifies the minimum and maximum allowed values.                                                                    |
| `platforms`   | Array   | (Optional) An array of strings (`"windows"`, `"unix"`). If present, this option is **only** available on the specified platforms.                        |
| `options`     | Array   | (Required for `type: "select"`) An array of objects, each with a `value` (the string to be used) and a `text` (the string to be displayed in the UI). |

### 5. Step-by-Step Guide to Creating a New Command

Let's create a definition for the `arp` command as an example. Its basic usage is to display the ARP table (`arp -a`).

**Step 1: Choose an Identifier and Basic Info**
The identifier will be `"arp"`. The name is "ARP Table" and the description is "Displays and modifies the IP-to-Physical address translation tables."

**Step 2: Identify the Target**
The basic `arp -a` command has no target. However, `arp` can take a hostname as a target for other operations. For a simple "display all" command, we can set `target` to `null`. If we wanted to support `arp <hostname>`, we would set `target` to `"host"`. Let's stick with `target: null` for now.

**Step 3: Define Platform-Specific Base Commands**
The base command is `"arp"` on both Windows and Unix.

```json
"arp": {
  "name": "ARP Table",
  "description": "Displays the IP-to-Physical address translation tables.",
  "target": null,
  "windows": {
    "base": "arp",
    "flags": { ... }
  },
  "unix": {
    "base": "arp",
    "flags": { ... }
  },
  "options": [ ... ]
}
```

**Step 4: Define the `options`**
The primary function we want to implement is displaying the table. This is done with the `-a` flag on both platforms. Let's create an option for this.

*   `id`: `"display_all"`
*   `label`: `"Display all entries"`
*   `type`: `"checkbox"`
*   It should be checked by default, so we'll add `"value": "true"`.

```json
"options": [
  {
    "id": "display_all",
    "label": "Display all entries",
    "type": "checkbox",
    "value": "true"
  }
]
```

**Step 5: Map Options to `flags`**
Now, we connect the `"display_all"` option to the platform-specific flags inside the `windows` and `unix` objects.

*   On both Windows and Unix, the flag is `-a`.
*   So, we add `"display_all": ["-a"]` to both `flags` objects.

```json
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
}
```

**Step 6: Assemble the Final Definition**

Putting it all together, the complete definition for our simple `arp` command is:

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

This definition will generate the command `arp -a` when the "Display all entries" checkbox (which is on by default) is used on either platform.

### Best Practices

*   **Consistency:** Use clear and consistent `id` values. The `id` is the glue between `options` and `flags`.
*   **Platform Specificity:** Pay close attention to differences in flags between Windows and Unix. Use the `platforms` key in an option when it's not universal. For example, `ping -t` (Windows) is equivalent to `ping` with no count limit (Unix), not a specific flag. The `continuous` option in the `ping` example handles this correctly.
*   **Define `options` First:** It is often easier to first list all the parameters a command can take in the `options` array, and then fill in the `flags` mappings for each platform.
*   **Validate:** Ensure your final output is valid JSON. A single misplaced comma can invalidate the entire file.