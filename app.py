from src.main import create_app
from src.config import config_instance

app = create_app(config=config_instance())

if __name__ == '__main__':
    app.run(debug=True)
