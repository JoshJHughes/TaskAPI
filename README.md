# TaskAPI

## Installation - pip

`pip install -r ./requirements.txt`

`fastapi run ./src/main.py  `

## Installation - Docker

`docker build -t taskapiimg .`

`docker run -d --name taskapicontainer -p 8000:8000 taskapiimg`

## Run tests

`pytest .`

## API Examples

### health check
`curl --request GET --url http://localhost:8000/health`

### create task
`curl --request POST --url http://localhost:8000/tasks \
--header 'Content-Type: application/json' \
--data '{
  "title": "title",
  "priority": "1",
  "due_date": "2025-09-18"
}'`

### get all tasks

`curl --request GET \
  --url 'http://localhost:8000/tasks?completed=false&priority=1' \
  --header 'Content-Type: application/json'`

### get task by id

`curl --request GET \
  --url http://localhost:8000/tasks/{task_id} \
  --header 'Content-Type: application/json'`

### update task by id

`curl --request PUT \
  --url http://localhost:8000/tasks/{task_id} \
  --header 'Content-Type: application/json \
  --data '{
  "description": "desc"
}'`

### delete task by id

`curl --request DELETE \
  --url http://localhost:8000/tasks/{task_id} \
  --header 'Content-Type: application/json'`