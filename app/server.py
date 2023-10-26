import os, sys

sys.path.append(os.path.abspath("./"))  # To single-handedly execute this script

import uvicorn

if __name__ == "__main__":
    config = uvicorn.Config("app.main:app", host="0.0.0.0", port=8000, reload=True)
    server = uvicorn.Server(config=config)
    server.install_signal_handlers = lambda: None  # this is the necessary workaround
    server.run()
