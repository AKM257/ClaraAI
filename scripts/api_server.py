from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run-pipeline-a', methods=['POST'])
def run_pipeline_a():
    result = subprocess.run(
        ['python', 'run_pipeline.py'],
        cwd=r'C:\Users\Anshit\Desktop\ClaraAI\ClaraAI\scripts',
        capture_output=True,
        text=True
    )
    return jsonify({
        'output': result.stdout,
        'errors': result.stderr,
        'status': 'success' if result.returncode == 0 else 'failed'
    })

@app.route('/run-pipeline-b', methods=['POST'])
def run_pipeline_b():
    result = subprocess.run(
        ['python', 'run_pipeline.py'],
        cwd=r'C:\Users\Anshit\Desktop\ClaraAI\ClaraAI\scripts',
        capture_output=True,
        text=True
    )
    return jsonify({
        'output': result.stdout,
        'errors': result.stderr,
        'status': 'success' if result.returncode == 0 else 'failed'
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'running'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)