from flask import Flask, render_template, request, Response, jsonify
import subprocess
import json
import platform
import uuid

app = Flask(__name__)

running_processes = {}

def load_commands():
    with open('commands.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_commands_by_platform(commands):
    """Filter commands based on current platform"""
    os_type = platform.system().lower()
    current_platform = 'windows' if os_type == 'windows' else 'unix'
    
    filtered_commands = {}
    
    for cmd_id, cmd_config in commands.items():
        if 'platforms' in cmd_config:
            if current_platform not in cmd_config['platforms']:
                continue 
        
        platform_config = cmd_config.get('windows' if current_platform == 'windows' else 'unix')
        if not platform_config:
            continue  
        
        filtered_options = []
        for option in cmd_config.get('options', []):
            if 'platforms' in option:
                if current_platform not in option['platforms']:
                    continue 
            filtered_options.append(option)
        
        filtered_cmd = cmd_config.copy()
        filtered_cmd['options'] = filtered_options
        filtered_commands[cmd_id] = filtered_cmd
    
    return filtered_commands

@app.route('/')
def index():
    commands = load_commands()
    filtered_commands = filter_commands_by_platform(commands)
    return render_template('index.html', commands=filtered_commands)

@app.route('/api/commands')
def get_commands():
    commands = load_commands()
    filtered_commands = filter_commands_by_platform(commands)
    return jsonify(filtered_commands)

@app.route('/api/platform')
def get_platform():
    """Endpoint to return current platform information"""
    os_type = platform.system().lower()
    return jsonify({
        'os': os_type,
        'platform': 'windows' if os_type == 'windows' else 'unix',
        'system': platform.system(),
        'machine': platform.machine(),
        'version': platform.version()
    })

@app.route('/execute/<tool>', methods=['POST'])
def execute_tool(tool):
    commands = load_commands()
    filtered_commands = filter_commands_by_platform(commands)
    
    if tool not in filtered_commands:
        return Response('Command not found or not supported on this platform', mimetype='text/plain')
    
    execution_id = str(uuid.uuid4())
    return Response(
        execute_command(tool, commands[tool], request.json, execution_id), 
        mimetype='text/plain',
        headers={'X-Execution-ID': execution_id}
    )

@app.route('/stop/<execution_id>', methods=['POST'])
def stop_execution(execution_id):
    if execution_id in running_processes:
        try:
            process = running_processes[execution_id]
            process.terminate()
            del running_processes[execution_id]
            return jsonify({'status': 'stopped'})
        except:
            return jsonify({'status': 'error'})
    
    return jsonify({'status': 'not_found'})

def execute_command(tool, config, data, execution_id):
    os_type = platform.system().lower()
    cmd_config = config.get('windows' if os_type == 'windows' else 'unix', config.get('command'))
    
    if not cmd_config:
        yield 'Command not supported on this system\n'
        return
    
    cmd = [cmd_config['base']]
    
    for option in config['options']:
        opt_id = option['id']
        value = data.get(opt_id)
        
        if 'platforms' in option:
            current_platform = 'windows' if os_type == 'windows' else 'unix'
            if current_platform not in option['platforms']:
                continue 
        
        if not value and option.get('required'):
            yield f'Error: {option["label"]} is required\n'
            return
        
        if value:
            if option['type'] == 'checkbox':
                if value:
                    flag = cmd_config['flags'].get(opt_id)
                    if flag:
                        if isinstance(flag, list):
                            cmd.extend(flag)
                        else:
                            cmd.append(flag)
            else:
                flag = cmd_config['flags'].get(opt_id)
                if flag:
                    if isinstance(flag, list):
                        cmd.extend(flag)
                        cmd.append(str(value))
                    else:
                        cmd.extend([flag, str(value)])
    
    target = data.get(config['target'])
    if target:
        cmd.append(target)
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        running_processes[execution_id] = process
        
        yield f'Executing: {" ".join(cmd)}\n'
        yield f'Execution ID: {execution_id}\n'
        yield f'System: {platform.system()} ({platform.machine()})\n\n'
        
        for line in iter(process.stdout.readline, ''):
            if execution_id not in running_processes:
                yield '\nExecution interrupted\n'
                break
            yield line
            
        process.wait()
        
        if execution_id in running_processes:
            del running_processes[execution_id]
            yield f'\nProcess finished with exit code: {process.returncode}\n'
        
    except Exception as e:
        if execution_id in running_processes:
            del running_processes[execution_id]
        yield f'Error: {str(e)}\n'

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
