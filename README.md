## How to run the project

Clone the project Repository
```
git clone git@github.com:tysjosh/flask-vending-machine-api.git

```

Enter the project folder and create a virtual environment
``` 
$ python -m venv venv 

```

Activate the virtual environment
``` 
$ source venv/bin/actvate #On linux Or Unix

$ venv/Scripts/activate.bat #On Windows 
 
```

Install all requirements

```
$ pip install -r requirements.txt
```

Create a .env and define all set up environment variables

```
export SECRET_KEY=........
export JWT_SECRET_KEY=........
export DEV_DATABASE_URI=...........
export PROD_DATABASE_URI=..........
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

