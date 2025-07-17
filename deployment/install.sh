#!/bin/bash

echo "========================================"
echo "ChatGLM3 Discord Bot Installer"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10+ from https://python.org"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python version: $PYTHON_VERSION"

# Extract major version
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
if [ "$MAJOR_VERSION" -lt 3 ]; then
    echo "ERROR: Python 3.10+ is required"
    exit 1
fi

# Create virtual environment
echo
echo "Creating virtual environment..."
if [ -d "chatglmbot-env" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf chatglmbot-env
fi

python3 -m venv chatglmbot-env
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source chatglmbot-env/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p models logs startup

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo
    echo "Creating .env file from template..."
    cp env.example .env
    echo
    echo "IMPORTANT: Please edit the .env file with your configuration:"
    echo "- Discord bot token"
    echo "- MySQL database credentials"
    echo "- Model path"
    echo
    echo "Opening .env file for editing..."
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    else
        echo "Please edit .env file manually"
    fi
fi

# Check if model file exists
if [ ! -f "models/chatglm3-6b.Q4_0.gguf" ]; then
    echo
    echo "WARNING: ChatGLM3 model file not found!"
    echo "Please download chatglm3-6b.Q4_0.gguf from:"
    echo "https://huggingface.co/TheBloke/ChatGLM3-6B-GGUF"
    echo "And place it in the models/ directory"
    echo
fi

# Create startup script
echo "Creating startup script..."
cat > startup/startup.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/.."
source chatglmbot-env/bin/activate
python main.py
EOF

chmod +x startup/startup.sh

# Create systemd service file (Linux only)
if command -v systemctl &> /dev/null; then
    echo "Creating systemd service file..."
    cat > startup/chatglm3-bot.service << EOF
[Unit]
Description=ChatGLM3 Discord Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/chatglmbot-env/bin/python $(pwd)/main.py
Restart=always
RestartSec=10
Environment=PATH=$(pwd)/chatglmbot-env/bin

[Install]
WantedBy=multi-user.target
EOF

    echo "To enable auto-startup on Linux:"
    echo "sudo cp startup/chatglm3-bot.service /etc/systemd/system/"
    echo "sudo systemctl enable chatglm3-bot.service"
    echo "sudo systemctl start chatglm3-bot.service"
fi

echo
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Download the AI model to models/ directory"
echo "3. Run: python main.py"
echo "4. For auto-startup, use: ./startup/startup.sh"
echo 