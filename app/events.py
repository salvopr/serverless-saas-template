from enum import Enum
from datetime import datetime
import calendar

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from dateutil.relativedelta import relativedelta

from app.exceptions import EventError
from config import current_config


class EventTypes(str, Enum):
    PAYMENT = 'PAYMENT'
    ACTIVITY = 'ACTIVITY'
    NEW_USER = 'NEW_USER'
    CHURN = 'CHURN'


def new_event(event_type, user, values=None, date_time=None):
    try:
        dynamodb = boto3.resource('dynamodb', region_name=current_config.AWS_REGION)
        table = dynamodb.Table(current_config.EVENT_TABLE)
        item = {"event_type": event_type,
                "datetime": str(datetime.utcnow() if not date_time else date_time),
                "user": user}
        if values:
            item.update(values)
        table.put_item(Item=item)
    except ClientError as e:
        raise EventError("cannot save event " + e.response['Error']['Message']) from e


def get_monthly_events(event_type, year, month):
    month_start = datetime(year, month, 1)
    month_end = datetime(year, month, calendar.monthrange(year, month)[1])
    try:
        dynamodb = boto3.resource('dynamodb', region_name=current_config.AWS_REGION)
        table = dynamodb.Table(current_config.EVENT_TABLE)
        condition = {"KeyConditionExpression": Key('event_type').eq(event_type) & Key('datetime').between(str(month_start), str(month_end))}
        r = table.query(**condition)
        data = r['Items']
        while "LastEvaluatedKey" in r:
            condition["ExclusiveStartKey"] = r['LastEvaluatedKey']
            r = table.query(**condition)
            data.extend(r['Items'])
        return data
    except ClientError as e:
        raise EventError("cannot get events " + e.response['Error']['Message']) from e


def paying_user_count_now():
    # this is a slow scan - think of adding a GSI to DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=current_config.AWS_REGION)
    table = dynamodb.Table(current_config.USERS_TABLE)
    r = table.scan()
    counter = len(r['Items'])
    while 'LastEvaluatedKey' in r:
        r = table.scan(ExclusiveStartKey=r['LastEvaluatedKey'])
        counter += len(r['Items'])
    return table.item_count


def _user_event_counter(year, month, event):
    data = get_monthly_events(event, year, month)
    user_set = set()
    for d in data:
        user_set.add(d['user'])
    return len(user_set)


def mau(year, month):
    return _user_event_counter(year, month, EventTypes.ACTIVITY)


def new_users_a_month(year, month):
    return _user_event_counter(year, month, EventTypes.NEW_USER)


def churned_users_a_month(year, month):
    return _user_event_counter(year, month, EventTypes.CHURN)


def churn(year, month):
    new_users_this_month = new_users_a_month(year, month)
    total_paying_users_this_month = paying_user_count_now()
    total_users_previous_month = total_paying_users_this_month - new_users_this_month
    churned_users_this_month = churned_users_a_month(year, month)
    non_churned_users_this_month = total_paying_users_this_month - churned_users_this_month
    return 1 - (non_churned_users_this_month/total_users_previous_month) if total_users_previous_month else 0


def arpu(year, month):
    data = get_monthly_events(EventTypes.PAYMENT, year, month)
    revenue = 0
    count = 0
    for d in data:
        revenue += d['amount_paid']
        count += 1
    return revenue / (100 * count)  # amount_paid is in cents so divide by 100


def ltv(year, month):
    return arpu(year, month)/churn(year, month)





