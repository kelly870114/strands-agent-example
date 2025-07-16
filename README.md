Go to the code-server instance that you launched earlier and open a terminal. Run the following commands

# Install UV and Python 3.12
cd ~
curl -LsSf https://astral.sh/uv/install.sh | sh
if [ "$SHELL" = "/bin/bash" ]; then
  echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
  echo 'eval "$(uvx --generate-shell-completion bash)"' >> ~/.bashrc
fi
source ~/.bashrc
uv self update
uv python install 3.12

# Setup Python Virtual Environment
## Create the requirements.txt file:
cat << EOF > requirements.txt
boto3
mcp[cli]
nova-act
opensearch-py
pandas
retrying
strands-agents 
strands-agents-tools[mem0_memory]
streamlit
tqdm
uv
EOF

# Install the Python libraries
uv venv
source ~/.venv/bin/activate
uv pip install -r requirements.txt

uv run 