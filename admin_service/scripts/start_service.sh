alembic upgrade head &&
python admin_service/cli.py create-user --name admin --email admin@mail.ru --password admin &&
uvicorn admin_service.main:app --host 0.0.0.0 --port 8000