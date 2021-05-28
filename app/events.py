from enum import Enum
from datetime import datetime
import calendar

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
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


class MonthlyKPIs:
    def __init__(self, month_end):
        self.month_end = month_end
        dynamodb = boto3.resource('dynamodb', region_name=current_config.AWS_REGION)
        self.users_table = dynamodb.Table(current_config.USERS_TABLE)
        self.events_table = dynamodb.Table(current_config.EVENT_TABLE)
        self.cache = {}

    def get_monthly_events(self, event_type):
        month_start = self.month_end - relativedelta(months=1)
        try:
            dynamodb = boto3.resource('dynamodb', region_name=current_config.AWS_REGION)
            table = dynamodb.Table(current_config.EVENT_TABLE)
            condition = {"KeyConditionExpression": Key('event_type').eq(event_type) & Key('datetime').between(str(month_start), str(self.month_end))}
            r = table.query(**condition)
            data = r['Items']
            while "LastEvaluatedKey" in r:
                condition["ExclusiveStartKey"] = r['LastEvaluatedKey']
                r = table.query(**condition)
                data.extend(r['Items'])
            return data
        except ClientError as e:
            raise EventError("cannot get events " + e.response['Error']['Message']) from e

    def _user_event_counter(self, event):
        data = self.get_monthly_events(event)
        user_set = set()
        for d in data:
            user_set.add(d['user'])
        return len(user_set)

    def mau(self):
        if 'mau' not in self.cache:
            self.cache['mau'] = self._user_event_counter(EventTypes.ACTIVITY)
        return self.cache['mau']

    def new_users(self):
        if 'new_users' not in self.cache:
            self.cache['new_users'] = self._user_event_counter(EventTypes.NEW_USER)
        return self.cache['new_users']

    def churned_users(self):
        if 'churned_users' not in self.cache:
            self.cache['churned_users'] = self._user_event_counter(EventTypes.CHURN)
        return self.cache['churned_users']

    def mrr(self):
        if 'mrr' not in self.cache:
            data = self.get_monthly_events(EventTypes.PAYMENT)
            revenue = 0
            count = 0
            for d in data:
                revenue += float(d['amount_paid'])
                count += 1
            self.cache['mrr'] = (revenue/100, count)
        return self.cache['mrr']  # amount_paid is in cents so divide by 100

    def churn(self):
        if "churn" not in self.cache:
            new_users_this_month = self.new_users()
            revenue, payment_count = self.mrr()
            total_paying_users_this_month = payment_count
            total_users_previous_month = total_paying_users_this_month - new_users_this_month
            churned_users_this_month = self.churned_users()
            non_churned_users_this_month = total_paying_users_this_month - churned_users_this_month
            self.cache['churn'] = 1 - (non_churned_users_this_month/total_users_previous_month) if total_users_previous_month else 0
        return self.cache['churn']

    def ltv(self):
        if "ltv" not in self.cache:
            mrr_now, count = self.mrr()
            arpu = mrr_now/count if count != 0 else 0
            _churn = self.churn()
            self.cache['ltv'] = arpu/_churn if _churn != 0 else 0
        return self.cache['ltv']

    def analyze(self):
        self.mau()
        self.mrr()
        self.ltv()
        self.churn()

