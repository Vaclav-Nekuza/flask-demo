# Flask Demo

## Purpose
Purpose of this document is to make an overview of this application

## Revisions
| version       | date          | author        |
|---------------|---------------|---------------|
| 1.0           | 4.5.2021      | Václav Nekuža |

## Introduction
Flask-demo is a Python3.8 application, that could be used as a storage of personal information.

Due to lack of security it should not be used with open access, as it is meant to represent my programing experience.   

## Endpoints
host(default): localhost
port(default): 5000
### POST address
Serves for inserting of separate address insert into database.   
url: `http://<host>:<port>/api/v1/address`  
payload:
```python  
{
  "street": str,
  "street_number": int,
  "post_code": int,
  "city": str,
  "country": str
}
```
Response:    
```python  
{
  "err_code": int,
  "message": str,
  "data": str
}
```

### POST person
Serves for inserting of people including an address.
url: `<host>/api/v1/personal`  
payload:
```python  
{
    "first_name": str,
    "surname": str,
    "address": {
        "street": str,
        "street_number": int,
        "post_code": int,
        "city": str,
        "country": str
    },
    "email": str,
    "date_of_birth": str
}
```

Response:  
```python  
{
  "err_code": int,
  "message": str,
  "data": str
}
```

### GET address
Serves to retrieve address from database.   
url: `<host>/api/v1/address`    
optional parameters:    
```  
id: int,  
street: str,   
street_number: int,   
post_code: int,  
city: str,   
country: str   
```
(example: `http://localhost:5000/api/v1/address?id=1`)  
!!!As for now the only two combination of parameters are only id or all the other combined.!!!    
Response: 
```python  
{
  "err_code": int,
  "message": str,
  "data": [
    {
      "id": int,
      "street": str,
      "street_number": int,
      "post_code": int,
      "city": str,
      "country": str
    }
  ]
}
```

### GET person
Serves to retrieve people from database.
url: `<host>/api/v1/personal`  
optional parameters:
```
id: int,
first_name: str,
surname: str,
email: str,
```
(example: `http://localhost:5000/api/v1/personal?first_name=test&surname=test`)  
Valid combinations of arguments:
```
1) No arguments
2) id
3) email
4) first_name, surname
```
Response: 
```python  
{
  "err_code": int,
  "message": str,
  "data": [
    {
      "id": int,
      "created": str,
      "first_name": str,
      "surname": str,
      "address": {
        "street": str,
        "street_number": int,
        "post_code": int,
        "city": str,
        "country": str
      },
      "email": str,
      "date_of_birth": str
    }
  ]
}
```

## Database structure
Database name: demo_db  
port(default): 5432  
Schema name: demo  

### People table  
| column        | data type     | constraints | example                    |
|---------------|---------------|-------------|----------------------------|
| id            | Integer       | unique      | 1                          |
| created       | ArrowType     | not null    | 2021-04-22 15:23:43.574457 |
| first_name    | String        | not null    | John                       |
| surname       | String        | not null    | Doe                        |
| address_id    | Integer       | not null    | 1                          |
| email         | String        | PK          | test@email.com             |
| date_of_birth | ArrowType     | not null    | 2000-04-23 00:00:00        |


### Address table  
| column        | data type     | constraints | example                    |
|---------------|---------------|-------------|----------------------------|
| id            | Integer       | unique      | 1                          |
| street        | String        | PK          | Husova                     |
| street_number | Integer       | PK          | 42                         |
| post_code     | Integer       | PK          | 60200                      |
| city          | String        | PK          | Brno                       |
| country       | String        | PK          | Czech Republic             |


## Error handling

### List of exceptions
name: name of the exception  
http_code: http response code   
err_code: internal code of an error   
occurrence: during what this error occurs   

| name               | http_code     | err_code      | occurrence                                  |
|--------------------|---------------|---------------|---------------------------------------------|
| DemoExcept         | http_code=404 | err_code=1000 | does not occur                              |
| EngineCreation     | http_code=500 | err_code=1001 | creating connector to database              |
| DBDoesNotExist     | http_code=500 | err_code=1002 | connecting to database                      |
| SchemaDoesNotExist | http_code=500 | err_code=1003 | creating schema                             |
| SelectError        | http_code=500 | err_code=1004 | selecting data from either table            |
| Inconsistency      | http_code=400 | err_code=1005 | inserting duplicate data, colliding with PK |
| TableNotDefined    | http_code=400 | err_code=1006 | should not occur, meant for developer       |
| InsertError        | http_code=400 | err_code=1007 | inserting data into either table            |