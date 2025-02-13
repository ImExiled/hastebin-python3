from urllib.parse import urlparse
from colorama import Fore, Back, Style
import logging
import datetime as date
from flask import Flask, jsonify, send_file, url_for, render_template, send_from_directory, request, redirect
from os import path
import pathlib
import random
import string
import os
from publicsuffix import PublicSuffixList # type: ignore


# Create a simple logger with colors so we can accurately log errors and such
class CustomFormatter(logging.Formatter):

    grey = f"{Style.DIM}{Fore.WHITE}"
    yellow = f"{Style.DIM}{Fore.YELLOW}"
    red = f"{Style.DIM}{Fore.RED}"
    bold_red = f"{Style.NORMAL}{Back.RED}{Fore.WHITE}"
    reset = f"{Fore.RESET}{Back.RESET}{Style.RESET_ALL}"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

def detect_language(filename):
    """Detects the programming language of a file based on its extension."""

    ext = filename.split('.').pop().lower() if '.' in filename else ""  # Handle files without extensions

    lang_map = {
        'js': 'javascript',
        'mjs': 'javascript',
        'jsx': 'jsx',
        'ts': 'typescript',
        'tsx': 'tsx',
        'py': 'python',
        'pyw': 'python',
        'c': 'c',
        'cpp': 'cpp',
        'cc': 'cpp',
        'cxx': 'cpp',
        'h': 'c',
        'hpp': 'cpp',
        'java': 'java',
        'kt': 'kotlin',
        'go': 'go',
        'rs': 'rust',
        'php': 'php',
        'php3': 'php',
        'php4': 'php',
        'php5': 'php',
        'php7': 'php',
        'php8': 'php',
        'rb': 'ruby',
        'swift': 'swift',
        'cs': 'csharp',
        'vb': 'vbnet',
        'vbs': 'vbscript',
        'html': 'html',
        'htm': 'html',
        'xhtml': 'xhtml',
        'css': 'css',
        'scss': 'scss',
        'sass': 'sass',
        'less': 'less',
        'xml': 'xml',
        'xsl': 'xsl',
        'xslt': 'xslt',
        'json': 'json',
        'yaml': 'yaml',
        'yml': 'yaml',
        'sql': 'sql',
        'md': 'markdown',
        'markdown': 'markdown',
        'txt': 'text',
        'sh': 'bash',
        'bash': 'bash',
        'zsh': 'zsh',
        'powershell': 'powershell',
        'bat': 'batch',
        'ps1': 'powershell',
        'lua': 'lua',
        'perl': 'perl',
        'pl': 'perl',
        'pm': 'perl',
        'r': 'r',
        'dart': 'dart',
        'groovy': 'groovy',
        'scala': 'scala',
        'erl': 'erlang',
        'elixir': 'elixir',
        'ex': 'elixir',
        'elm': 'elm',
        'clojure': 'clojure',
        'lisp': 'lisp',
        'el': 'lisp',
        'scm': 'scheme',
        'go': 'go',
        'rs': 'rust',
        'swift': 'swift',
        'kt': 'kotlin',
        'ts': 'typescript',
        'cs': 'csharp',
        'vb': 'vbnet',
        'vbs': 'vbscript',
        'lua': 'lua',
        'perl': 'perl',
        'pl': 'perl',
        'pm': 'perl',
        'r': 'r',
        'dart': 'dart',
        'groovy': 'groovy',
        'scala': 'scala',
        'erl': 'erlang',
        'elixir': 'elixir',
        'ex': 'elixir',
        'elm': 'elm',
        'clojure': 'clojure',
        'lisp': 'lisp',
        'el': 'lisp',
        'scm': 'scheme',

        # Add more as needed...
    }

    return lang_map.get(ext)  # Use .get() to return None if not found

psl = PublicSuffixList()  # Initialize the Public Suffix List

def get_root_domain(url):
    """
    Extracts the root domain from a URL using the Public Suffix List.
    """
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        if hostname:
          return psl.get_tld(hostname)
        return None  # Handle cases where hostname is None
    except Exception as e:
        print(f"Error parsing URL: {e}") #Important for debugging
        return None

# Let's create the webserver
app = Flask(__name__, static_url_path='/static')

@app.route('/', methods=["POST"])
def save_code():
    code = request.form.get('code')
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) + ".haste"

    filename = os.path.basename(filename)
    if not filename:
        filename = ''.join(random.choices(string.ascii_letters + string.digits, k=16))


    filepath = os.path.join("files", filename)
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    try:
        os.makedirs("files", exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(code)
            return jsonify({'redirect_url': f'/?f={os.path.splitext(filename)[0]}'})
        #return jsonify({'message': f'Code saved to {filename}'}), 200
    except Exception as e:
        # Handle the exception and return an error message
        return jsonify({'error': str(e)}), 500

@app.route("/", methods=['GET'])
def index():
    if request.values.get('f') is None or request.values.get('f') == "":
        return render_template('index.html', isFile=False)
    else:
        ourLanguage = detect_language(request.values.get('f'))
        if request.values.get("f") is None or request.values.get("f") == "":
            return render_template('index.html', isFile=False)

        if ourLanguage == None:
            ourLanguage = "text"
        else:
            pass
        ourFileName = os.path.splitext(request.values.get("f"))[0]
        if not os.path.isfile(f'./files/{ourFileName}.haste'):
            return render_template('index.html', isFile=False)
        with open(f'./files/{ourFileName}.haste', 'r') as f:
            return render_template('index.html', code=f.read(), filelang=ourLanguage, isFile=True)
        
# API endpoints
@app.route('/api/getpaste', methods=["GET"])
def getpaste():
    fileRequest = request.values.get("haste")
    if os.path.isfile(f"./files/{fileRequest}.haste"):
        with open(f'./files/{fileRequest}.haste', 'r') as f:
            return send_file(f"./files/{fileRequest}.haste", as_attachment=True)
    else:
        return "404"
    
@app.route('/api/haste', methods=["POST"])
def putpaste():
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    hasteToPaste = request.json
    filepath = os.path.join("files", filename)
    os.makedirs("files", exist_ok=True)
    logger.warning(hasteToPaste)
    currentUrl = request.url
    rootDomain = get_root_domain(currentUrl)
    #return hasteToPaste['data']
    with open(filepath, 'w') as f:
        f.write(hasteToPaste["data"])
        return jsonify({'response': f'{os.path.splitext(filename)[0]}', 'status': 'success'})