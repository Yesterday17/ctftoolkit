from flask import Flask, render_template, request, redirect
import json

app = Flask(__name__)

files = {}

scheme = 'https'
host = 'ctf.mmf.moe'
port = '7192'
persist = 'files.json'


@app.route('/dtd/<file>', methods=['GET'])
def get_dtd(file):
    if file in files:
        f = files[file]
        return render_template('dtd.html', file=f)
    return 'No file got'


@app.route('/dtd/new', methods=['GET'])
def add_dtd():
    file = {
        'lang': {'java': False, 'php': False}
    }
    language = request.args.get('lang')
    if language == 'java':
        # Java
        file['lang']['java'] = True
    elif language == 'php':
        # PHP
        file['lang']['php'] = True

        # php filter: base64
        b64 = request.args.get("base64")
        if b64 is not None:
            file['base64'] = True
    else:
        # Unsupported
        return 'Unsupported language.'

    file['url'] = request.args.get('url')
    if file['url'] is None or file['url'] == '':
        return 'No url defined'

    file['domain'] = request.args.get('domain')
    if file['domain'] is None or file['domain'] == '':
        return 'No domain specified.'

    file['port'] = request.args.get('port')
    if file['port'] is None or file['port'] == '':
        return 'No port specified.'

    filename = str(len(files)) + '.dtd'
    file['name'] = filename
    files[filename] = file
    save()

    return redirect("/dtd/%s" % filename)


@app.route("/payload/<file>")
def payload(file):
    return render_template('payload.html', scheme=scheme, host=host, port=port, file=file)


@app.route("/")
def index():
    return render_template("index.html", files=files.values())


def load():
    global files
    try:
        file = open(persist, 'r', encoding='utf-8')
        files = json.load(file)
    finally:
        return


def save():
    file = open(persist, 'w', encoding='utf-8')
    json.dump(files, file, ensure_ascii=False)
    file.close()


if __name__ == '__main__':
    load()
    app.run(port=port)
