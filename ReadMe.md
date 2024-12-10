# vLLM Server Flask Manager
This repository here serves as a simple Flask wrapper so that team members can call the `/reset` endpoint to restart a certain vLLM instance.

To run this simply use cURL on the same instance and run:
```
curl -X POST -H "Content-Type: application/json" -d '{
    "username": <string-of-username>,
    "vllm_download_dir": <download-dir-of-existing-vLLM-model>,
    "log_file": <location-of-shared-log-file>
}' http://localhost:5000/reset
```

Currently it's only set towards running Llama 3.3, but this repository can easily be extended for switching between any huggingface model. In that case, careful consideration is needed in developing:
1. Making the string os safe since we'll be running user input if we allow switching between any huggingface model. Maybe consider only allowing users to choose between some chosen set of models
2. The storage of the models themselves will depend on where they're stored and might be space constrained. Consider deleting other huggingface models if you need to download a new one.

## Setup
Install the `requirements.txt` using `pip`. If any issues arise from async, try running `pip install flask[async]`.

