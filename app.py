from flask import Flask
from app.routes import routes

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Register blueprints
    app.register_blueprint(routes)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)