# Project Resource Scheduler

**Assignment:**
To understand the what applictaion do and what solution it provide, check out the given docx link:
[View Full Documentation](project_resource_scheduler/Developer-Assessment 3-Resource Skill matching.docx)

## How to start application

1. **Create Pipenv env [Installation of pipenv in your respective OS](https://pipenv.pypa.io/en/latest/installation.html):**
```commandline
pipenv install

# To activate this project's virtualenv, run pipenv shell.
# Alternatively, run a command inside the virtualenv with pipenv run.
# Installing dependencies from Pipfile.lock (a2f100)...

pipenv shell

# Launching subshell in virtual environment...
```

2. **In the Activate Terminal, Install requirements:** 
```commandline
pipenv install django
pipenv install djangorestframework
pipenv install django-debug-toolbar
```

3. **Run migrations commands:**
```commandline
python manage.py makemigrations

python manage.py migrate
```

4. **Upload the Dummy data in Database**

```commandline
# To upload Skill dataset

python manage.py loaddata dump_data/
```

## Database Design

- Database is used in design "SQLite3"
- 

