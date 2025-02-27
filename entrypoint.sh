#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "🔴 Retrieve deepseek model..."
ollama run deepseek-r1:7b
echo "🟢 Done!"

# Wait for Ollama process to finish.
wait $pid