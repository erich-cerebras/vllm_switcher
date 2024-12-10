from flask import Flask, request
import argparse
import asyncio
import os
import time
import subprocess

app = Flask(__name__)

lock = asyncio.Lock()

# finds whether the vllm exists, if it does, stop
def is_vllm_running(username):
    try:
        cmd = f'ps -ef | grep "vllm serve" | grep {username} | grep -vw grep'
        output = subprocess.check_output(cmd, shell=True)
        output = output.decode('utf-8')
        return True
    except subprocess.CalledProcessError as e:
        error_msg = f"Error executing command: {e}\n"
        print(error_msg)
        return False

def kill_and_wait(pid):
    try:
        os.kill(pid, 9)
        return_code = os.waitpid(pid, 0)[1]
        return str(return_code)
    except OSError as e:
        error = f"Error killing and waiting for PID: {e}"
        return error

def run_subprocess(cmd, vllm_download_dir, output_file):
    try:
        with open(output_file, 'w') as f:
            process = subprocess.Popen(cmd, stdout=f, stderr=f)
            return process.pid
    except Exception as e:
        print(f"Error while running command: {e}")
        return None

@app.route("/reset", methods=['POST'])
async def reset():
    if lock.locked():
        return "vLLM server is already running, currently locked..."

    # now get the JSON input of the user's name so that we can find their name
    data = request.get_json()
    if not data or "username" not in data or "vllm_download_dir" not in data or "log_file" not in data:
        return "Error, invalid input", 400

    print(data["username"], data["vllm_download_dir"], data["log_file"])

    async with lock:
        # find all processes that have vllm serve in it, and with the specific username but not the grep processes we just created
        if is_vllm_running(data["username"]):
            return "vLLM server is already running!"

        # respawn it if we aren't running, and keep it
        cmd = f'vllm serve meta-llama/Llama-3.3-70B-Instruct --tensor-parallel-size 4 --max-model-len 16384 --api-key serving-on-vllm --download_dir {data["vllm_download_dir"]} --port 8000'.split(" ")
        vllm_pid = run_subprocess(cmd, data["vllm_download_dir"], data["log_file"])
        return f"PID: {vllm_pid}\n"

def main():
    parser = argparse.ArgumentParser()
    args_env = [
        ("--port", int, 5000, "Specify the port to run the reset server")
    ]

    for arg, type_, default, help_text in args_env:
        parser.add_argument(arg, type=type_, default=default, help=help_text)
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port)

if __name__ == '__main__':
    main()
