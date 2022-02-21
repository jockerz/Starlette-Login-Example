## Installation

```shell
virtualenv -ppython3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```shell
uvicorn app_starlette:app --reload
```

## Login

 - Regular User: `user` : `password`
 - Admin User: `admin` : `password`
