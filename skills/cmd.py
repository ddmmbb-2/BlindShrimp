import subprocess

SKILL_NAME = 'CMD'
# 換成英文描述，讓大腦 (Planner) 閱讀更直覺
SKILL_DESC = 'Execute Windows terminal commands (e.g., dir, python script.py, etc.). Use this ONLY when you need to interact with the local operating system or file system.'

def execute(action_content, target_file='', **kwargs):
    try:
        # action_content 就是 AI 決定要執行的終端機指令
        result = subprocess.run(action_content, shell=True, capture_output=True, text=True, timeout=15)
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if error and not output: 
            return f'Execution Error: {error[:300]}'
            
        return output[:500] if output else 'Command executed successfully, but no text output was returned.'
        
    except subprocess.TimeoutExpired:
        return 'Execution Error: Command timed out after 15 seconds.'
    except Exception as e:
        return f'CMD Crashed: {str(e)}'