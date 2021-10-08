import json
import traceback
from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.user import User
from . import email_blueprint


@email_blueprint.route('/ses_notifications', methods=["POST"])
def ses_notifications():
    notification = json.loads(request.get_data().decode('utf-8'))
    if notification.get('Type') == 'SubscriptionConfirmation':
        print(notification)  # it will contain subscription confirmation URL
    else:
        try:
            message = notification
            if 'bounce' in message and message['bounce']["bounceType"] == "Permanent":
                for bounce_data in message['bounce']['bouncedRecipients']:
                    email = bounce_data["emailAddress"]
                    user = User.load(email)
                    user.unsubscribe(bounce_data.get("diagnosticCode", "permanent bounce"))
            if 'complaint' in message:
                for complaint_data in message['complaint']['complainedRecipients']:
                    email = complaint_data["emailAddress"]
                    user = User.load(email)
                    user.unsubscribe("complaint " + message['complaint'].get('complaintFeedbackType', "no feedback"))
        except Exception as e:
            traceback.print_exc()
            print(f"failed to process SES notification {notification}")
            raise Exception('SES callback error ') from e
    return ''


@email_blueprint.route('/unsubscribe', methods=["GET"])
@login_required
def unsubscribe():
    current_user.unsubscribe("manual")
    flash("You have been unsubscribed from future emails", "success")
    return redirect(url_for("payments_blueprint.index"))
