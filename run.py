from app import create_app

app = create_app()

# Expose app directly for Gunicorn
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)