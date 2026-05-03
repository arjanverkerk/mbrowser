require "os"
mp.command(string.format("run python3 %s/worker.py", os.getenv("MBROWSER_HOME")))
