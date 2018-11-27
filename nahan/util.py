from datetime import datetime
import re
from flask import url_for
from flask_babel import gettext
from .model import User,Notify
from . import db
from .voice import voice as voice_blueprint

def add_user_links_in_content(content_rendered):
    for at_name in re.findall(r'@(.*?)(?:\s|</\w+>)', content_rendered):
        receiver_u = User.query.filter_by(username=at_name).first()

        if not receiver_u:
            continue

        content_rendered = re.sub('@%s' % at_name,
                                  '@<a herf="%s" class="mention">%s</a>' % (url_for('user.info', uid=receiver_u.uid), at_name),
                                  content_rendered)

    return content_rendered


def add_notify_in_content(content, sender_id, topic_id, comment_id=None, append_id=None):
    valid_receiver = []
    for at_name in re.findall(r'@(.*?)(?:\s|s)', content):
        receiver_u = User.query.filter_by(username=at_name).first()
        if receiver_u:
            valid_receiver.append(receiver_u)

    valid_receiver = set(valid_receiver)
    all_notifies = []
    for u in valid_receiver:
        all_notifies.append(Notify(sender_id=sender_id,receiver_id=u.id,
                                   topic_id=topic_id, comment_id=comment_id,
                                   append_id=append_id))
    for new_notify in all_notifies:
        db.session.add(new_notify)

    db.session.commit()

    for i,u in enumerate(valid_receiver):
        if u.unread_notify:
            u.unread_notify = "%d,%s" % (all_notifies[i].id, u.unread_notify)
        else:
            u.unread_notify = "%d" % all_notifies[i].id

    db.session.commit()


@voice_blueprint.app_template_filter()
def natural_time(dt):
    """ Returns string representing "time since", 3 days ago, 5 hours ago etc.

    For datetime values, returns a string representing how many seconds,
    minutes or hours ago it was – falling back to the timesince format
    if the value is more than a day old.
    """
    now = datetime.now()
    # print "-->", now   2016-07-18 09:27:25.840414
    # print "---", dt    2016-07-18 09:27:26
    # The dt is truncated to seconds when saved in mysql.  So sometimes now may be small than dt.
    diff = now - dt if now >= dt else now - now

    periods = (
        (diff.days / 365, gettext("year"), gettext("years")),
        (diff.days / 30, gettext("month"), gettext("months")),
        (diff.days / 7, gettext("week"), gettext("weeks")),
        (diff.days, gettext("day"), gettext("days")),
        (diff.seconds / 3600, gettext("hour"), gettext("hours")),
        (diff.seconds / 60, gettext("minute"), gettext("minutes")),
        (diff.seconds, gettext("second"), gettext("seconds")),
    )

    for period, singular, plural in periods:
        if period:
            return "%d %s%s" % (period, singular if period == 1 else plural, gettext(' ago'))

    return gettext("just now")
