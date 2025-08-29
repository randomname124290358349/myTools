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

@app.route('/')
def index():
    commands = load_commands()
    return render_template('index.html', commands=commands)

@app.route('/api/commands')
def get_commands():
    return jsonify(load_commands())

@app.route('/execute/<tool>', methods=['POST'])
def execute_tool(tool):
    commands = load_commands()
    if tool not in commands:
        return Response('Comando não encontrado', mimetype='text/plain')
    
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
        yield 'Comando não suportado neste sistema\n'
        return
    
    cmd = [cmd_config['base']]
    
    for option in config['options']:
        opt_id = option['id']
        value = data.get(opt_id)
        
        if not value and option.get('required'):
            yield f'Erro: {option["label"]} é obrigatório\n'
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
        
        yield f'Executando: {" ".join(cmd)}\n'
        yield f'ID da execução: {execution_id}\n\n'
        
        for line in iter(process.stdout.readline, ''):
            if execution_id not in running_processes:
                yield '\nExecução interrompida\n'
                break
            yield line
            
        process.wait()
        
        if execution_id in running_processes:
            del running_processes[execution_id]
            yield f'\nProcesso finalizado com código: {process.returncode}\n'
        
    except Exception as e:
        if execution_id in running_processes:
            del running_processes[execution_id]
        yield f'Erro: {str(e)}\n'

if __name__ == '__main__':
    app.run(debug=True, threaded=True)