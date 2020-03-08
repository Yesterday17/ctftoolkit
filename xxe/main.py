from flask import Flask, render_template, request, redirect
import json
from utils import valid, exist

app = Flask(__name__)

files = {}

scheme = 'https'
host = 'ctf.mmf.moe'
port = '7192'
persist = 'files.json'


@app.route('/dtd/<file>', methods=['GET'])
def get_dtd(file):
    if file in files:
        # static files
        f = files[file]
    else:
        # dynamic generate files
        f = {
            'lang': {'java': False, 'php': False}
        }
        url = ''
        # protocol
        if exist(request.args.get('f')):
            url += 'file'
        elif exist(request.args.get('j')):
            url += 'jar'
            f['lang']['java'] = True
        elif exist(request.args.get('p')):
            url += 'php'
            f['lang']['php'] = True
        elif exist(request.args.get('ft')):
            url += 'ftp'
        else:
            return "No url scheme specified."
        url += '://'
        if valid(request.args.get('fu')):
            url += request.args.get('fu')
        else:
            return "No url content specified."
        f['url'] = url

        # language
        if not f['lang']['java'] and not f['lang']['php']:
            if exist(request.args.get('lj')):
                f['lang']['java'] = True
            elif exist(request.args.get('lp')):
                f['lang']['php'] = True
            elif exist(request.args.get('lpb')):
                f['lang']['php'] = True
                f['base64'] = True
            else:
                return "No language specified."
        f['domain'] = host
        f['port'] = port

    return render_template('dtd.html', file=f)


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
        if valid(b64):
            file['base64'] = True
    else:
        # Unsupported
        return 'Unsupported language.'

    file['url'] = request.args.get('url')
    if valid(file['url']):
        return 'No url defined'

    file['domain'] = request.args.get('domain')
    if valid(file['domain']):
        return 'No domain specified.'

    file['port'] = request.args.get('port')
    if valid(file['port']):
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
