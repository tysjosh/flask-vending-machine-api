## How to run the project

Clone the project Repository
```
git clone git@github.com:tysjosh/flask-vending-machine-api.git

```

Enter the project folder and create a virtual environment
``` 
$ python -m venv env 

```

Activate the virtual environment
``` 
$ source env/bin/actvate #On linux Or Unix

$ source env/Scripts/activate #On Windows 
 
```

Install all requirements

```
$ pip install -r requirements.txt
```

Run the project in development
```
$ export FLASK_APP=src/

$ export FLASK_DEBUG=1

$ flask run

```
Or 
``` 
python manage.py
``` 

