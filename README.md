# Django Challenge

Coding challenge written with Django Framework. 

This project assumes you had already installed these tools:
1. [python v3.6 or higher](https://www.python.org/downloads/release/python-367/)
2. [pip](https://www.makeuseof.com/tag/install-pip-for-python/)
3. [postgresql](http://postgresguide.com/setup/install.html)

Third party packages, tools, etc:
1. [bcrypt](https://pypi.org/project/bcrypt/) for encryption of passwords.
2. [clearbit](https://pypi.org/project/clearbit/) for getting additional data on emails.
3. [psycopg2](https://pypi.org/project/psycopg2/) for interacting with postgresql.
4. [pyhunter](https://github.com/VonStruddle/PyHunter) for check email validity.
5. [PyJWT](https://pyjwt.readthedocs.io/en/latest/) for authentication.

### API Usage

In order to use the API, you need a living postgresql instance on your local machine with these properties:
* name_of_database: **socialnetwork**
* user: **dummy**
* password: **123456**

In order to use django with postgresql, you need to follow this [link](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04).

First we need to create a `virtualenv` by using below commands:
* `virtualenv venv -p [python3 location like /usr/local/bin/python3]`
* `source venv/bin/activate`
* Go to the project directory like `cd /home/challenge-directory/`
* `pip install -r requirements.txt`

Below are the commands that is need for populating the empty postgresql table, then running the API:
* `python manage.py makemigrations socialnetwork`
* `python manage.py migrate`
* `python manage.py runserver`

There are different endpoints for this API:

1. `/signup`
    * This endpoint accepts *POST* request.
    * If user data is not on db it hashes the password, inserts the user data into db and returns a **token**.
    * Body Params:
    ```
    {
        "name": "dummy",
        "email": "dummy@gmail.com",
        "password": "123456"
    }
    ```

2. `/login`
    * This endpoint accepts *POST* request.
    * If user data is on db, it returns a **token**.
    * Body Params:
    ```
    {
        "email": "dummy@gmail.com",
        "password": "123456"
    }
    ```

3. `/create`
    * This endpoint accepts *POST* request.
    * `x-access-token` should be on header.
    * Body Params:
    ```
    {
        "content": "Lorem ipsum dolor sit amet"
    }
    ```

4. `/like`
    * This endpoint accepts *POST* request.
    * `x-access-token` should be on header.
    * Body Params:
    ```
    {
        "post_id": 5
    }
    ```
5. `/unlike`
    * This endpoint accepts *POST* request.
    * `x-access-token` should be on header.
    * Body Params:
    ```
    {
        "post_id": 5
    }
    ```

Additional Information:
* There are also 7 different endpoints other than the endpoints above and used for helper endpoints of automated bot and debugging.
* You could find a sample **POSTMAN** json file in the directory.

### AUTOMATED BOT
For this part, again you need to activate virtualenv and install requirements.

Bot Configuration File:
```
{
  "number_of_users": 4,
  "max_posts_per_user": 4,
  "max_likes_per_user": 4,
  "api_url": "http://localhost:8000"
}

```
Sample bot start command (You should give the bot config location as --file parameter):
* `python automated_bot.py --file config.json`

Tools used for deploying and serving endpoints:
1. [Microsoft Azure VM](https://azure.microsoft.com/tr-tr/services/virtual-machines/)
2. [gunicorn](https://gunicorn.org/)
3. [nginx](https://www.nginx.com/)
4. [supervisor](http://supervisord.org/introduction.html)
