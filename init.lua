require "os"
mp.command(string.format("run python %s/worker.py", os.getenv("MBROWSER_HOME")))
