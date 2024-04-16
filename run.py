from web.create_app import app


def main():
    app.run(host="0.0.0.0", debug=True, use_reloader=True, port=6001)


if __name__ == '__main__':
    main()
# gunicorn -c gunicorn_config.py run:app