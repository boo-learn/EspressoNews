### Run service
`docker compose up -d admin-service`

_Note: when the service starts, a new user is automatically created_ 

username: **admin** \
email: **admin@mail.ru** \
password: **admin**

### Use api
api local-url 'http://127.0.0.1:8000/docs'

_Note: when authorizing, in the **username field**, enter the **email**. \
Yes, this is a minor bug, we will fix it soon._

### Run tests
install requirements `pip install -r admin_service/requirements/txt` \
run tests `pytest -v admin_service/tests/api/`