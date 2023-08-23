from flask import Flask

app = Flask(__name__,
            static_url_path='',
            static_folder='public/tarot/static',
            template_folder='public/tarot/templates')


if __name__ == '__main__':
    # host='0.0.0.0' allows external access
    app.run(host='0.0.0.0')
