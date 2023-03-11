# HAI backend

## Dependencies

1. Create virtual environment in the repository
```
python -m virtualenv venv
```

2. Activate virtual environment (on mac, I am unsure of the command on Windows)
```
source venv/bin/activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. *[During Development]* Add new dependencies
```
pip freeze > requirements.txt
```
Note: this will overwrite the existing requirements file, so ensure that the requirements in the previous file are already installed in your virtualenv


## Setup & run server

The server is a simple flask application. By default, you can only access flask from your localhost,
but there are ways to workaround this. It is probably best for us to use [ngrok](http://ngrok.com), an application
that creates a public tunnel to your machine. This way, the frontend will point to the public ngrok URL (that anyone can
access, not just those on your localhost).
 
### ngrok (required for public access,, not necessary for local development)
1. Create an ngrok account
2. Download the ngrok binary and move it into this repository: https://dashboard.ngrok.com/get-started/setup. Be sure to add your account key!

### flask server
1. Ensure that you've sourced the virtual environment
2. run `FLASK_ENV=development FLASK_APP=server.py flask run --port 5000`. This runs a flask application defined in server.py on the port 5000. You should be able to visit http://localhost:5000 in your web browser if this was successful.
3. [optional] expose local server to public-facing address via ngrok. Simply run `ngrok http 5000` in a new terminal to create the tunnel. Documentation for ngrok is here: https://ngrok.com/docs/using-ngrok-with/flask/
