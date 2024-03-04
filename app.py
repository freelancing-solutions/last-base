from src.main import create_app
from src.config import create_config

app = create_app(config=create_config())

if __name__ == '__main__':
    app.run(debug=True)