import boto3
import json
from custom_encoder import CustomEncoder
import logging
logger = logging.getLogger()
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
        response = getBook(event['queryStringParameters']['bookId'])
    elif httpMethod == getMethod and path == booksPath:
        response = getBooks()
    elif httpMethod == postMethod and path == bookPath:
        response = saveBook(json.loads(event['body']))
    elif httpMethod == patchMethod and path == bookPath:
        requestBody = json.loads(event['body'])
        response = modifyBook(requestBody['bookId'], requestBody['updateKey'], requestBody['updateValue'])
    elif httpMethod == deleteMethod and path == bookPath:
        requestBody = json.loads(event['body'])
        response = deleteBook(requestBody['bookId'])
    else:
        response = buildResponse(404, 'Not Found')
    
    return response

def getBook(bookId):
    try:
        response = table.get_item(
            Key={
                'bookId': bookId
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'BookId: %s not found' % bookId})
    except:
        logger.exception('An exception has occured')

def getBooks():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])

        body = {
            'books': result
        }

        return buildResponse(200, body)

    except:
        logger.exception('An exception has occured')

def saveBook(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200, body)
    except:
       logger.exception('An exception has occured') 

def modifyBook(bookId, updateKey, updateValue):
    try:
        response = table.update_item(
            Key={
                'bookId': bookId,
            },
            UpdateExpression=' set %s = :value' % updateKey,
            ExpressionAttributeValues={
                ':value': updateValue
            },
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('An exception has occured')

def deleteBook(bookId):
    try:
        response = table.delete_item(
            Key={
                'bookId':bookId
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message':'SUCCESS',
            'deletedItem': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('An exception has occured')

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
