import boto3
import json
from custom_encoder import CustomEncoder
import logging
logger = loggin.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'books-db'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
bookPath = '/book'
booksPath = '/books'


def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == getMethod and path == bookPath:
        repsonse = getProduct(event['queryStringParameters']['bookId'])
    elif httpMethod == getMethod and path == booksPath:
        response = getProducts()
    elif httpMethod == postMethod and path == bookPath:
        response = saveBook(json.loads(event['body']))
    elif httpMethod == patchMethod and path == bookPath:
        requestBody = json.loads(event['body'])
        response = modifyBook(requestBody['booksId'], requestBody['updateKey'], requestBody['updateValue'])
    elif httpMethod == deleteMethod and path == bookPath:
        requestBody = json.loads(event['body'])
        response = deleteProduct(requestBody['bookId'])
    else:
        response = buildResponse(404, 'Not Found')
    
    return response


def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response

#17:30
