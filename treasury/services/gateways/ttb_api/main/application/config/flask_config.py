from gunicorn.app.base import BaseApplication
import uvicorn

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

class FlaskConfig:
    @classmethod
    def serve(cls, app_import_string: str, port: int = 8080, workers: int = 4) -> None:
        uvicorn.run(app_import_string, host="0.0.0.0", port=port, workers=workers, loop="uvloop", access_log=False)
