from flask import render_template,request,redirect,url_for,current_app,abort
from . import voice
from flask_login import login_required,current_user
from ..model import Topic,Comment,Node
from flask_babel import gettext
from flask_paginate import Pagination
from ..util import add_user_links_in_content,add_notify_in_content
from .. import db

@voice.route('/')
def index():
    per_page = current_app.config['PER_PAGE']
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page

    topics_all = Topic.query.filter_by(deleted=False).order_by(Topic.time_created.desc()).limit(per_page + offset)
    topics = topics_all[offset:offset + per_page]
    pagination = Pagination(page=page, total=Topic.query.count(),
                            per_page=per_page,
                            record_name='topics',
                            CSS_FRAMEWORK='bootstrap',
                            bs_version=3)
    return render_template('voice/index.html',
                           topics=topics,
                           title=gettext('Latest Topics'),
                           post_list_title=gettext('Latest Topics'),
                           pagination=pagination)

@voice.route('/voice/hot')
def hot():
    per_page = current_app.config['PER_PAGE']
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page

    topics_all = Topic.query.filter_by(deleted=False).order_by(
        Topic.reply_count.desc(), Topic.click.desc()).limit(per_page + offset)

    topics = topics_all[offset:offset + per_page]
    pagination = Pagination(page=page, total=Topic.query.count(),
                            per_page=per_page,
                            record_name='topics',
                            CSS_FRAMEWORK='bootstrap',
                            bs_version=3)
    return render_template('voice/index.html',
                           topics=topics,
                           title=gettext('Hottest Topics'),
                           post_list_title=gettext('Hottest Topics'),
                           pagination=pagination)
@voice.route("/nodes")
def all_nodes():
    return render_template('voice/node_all.html',
                           title=gettext('All nodes'),
                           nodes=Node.query.filter_by(deleted=False).all())


@voice.route('/node/view/<int:nid>')
def node_view(nid):
    n = Node.query.filter_by(id=nid, deleted=False).first_or_404()
    print(n)
    node_title = n.title
    per_page = current_app.config['PER_PAGE']
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page

    topics_all = Topic.query.filter_by(node_id=nid, deleted=False).order_by(Topic.time_created.desc()).limit(per_page+offset)
    topics = topics_all[offset:offset+per_page]
    pagination = Pagination(page=page,
                            total=Topic.query.filter_by(node_id=nid).count(),
                            per_page=per_page,
                            record_name='topics',
                            CSS_FRAMEWORK='bootstrap',
                            bs_version=3)
    return render_template('voice/node_view.html',
                           topics=topics,
                           title=gettext('Node view'),
                           post_list_title=gettext('Node ') + node_title + gettext("'s topics"),
                           pagination = pagination)
    return render_template('voice/node_view.html')


@voice.route("/voice/create", methods=['GET', 'POST'])
@login_required
def create():
    print(request.method)
    if request.method == 'GET':
        return render_template('voice/create.html', title=gettext('Create Topic'),
                               nodes=Node.query.filter_by(deleted=False).all())
    elif request.method == 'POST':
        _form = request.form
        title = _form['title']
        content = _form['content']
        node_id = _form['node']
        user_id = current_user.uid

        new_topic = Topic(user_id=user_id, title=title, content=content,node_id=node_id)
        new_topic.content_rendered = add_user_links_in_content(new_topic.content_rendered)

        db.session.add(new_topic)
        db.session.commit()
        topic_id = new_topic.tid

        add_notify_in_content(new_topic.content, current_user.uid, topic_id)

        current_user.add_topic(topic_id)
        Node.query.filter_by(id=node_id).first().add_topic(topic_id)
        db.session.commit()

        return redirect(url_for('voice.view', tid=topic_id))
    else:
        abort(404)


@voice.route('/voice/view/<int:tid>', methods=['GET', 'POST'])
def view(tid):
    per_page = current_app.config['PER_PAGE']
    topic = Topic.query.filter_by(tid=tid).first_or_404()
    if topic.deleted:
        abort(404)
    live_comments_all = list(
        filter(lambda x: not x.deleted, topic.extract_comments()))
    page = int(request.args.get('page', 1))
    offset = (page -1)*per_page
    live_comments = live_comments_all[offset:offset+per_page]
    pagination = Pagination(page=page,total=len(live_comments_all),
                            per_page=per_page,
                            record_name='live_comments',
                            CSS_FRAMEWORK='bootstrap',
                            bs_version=3)
    if request.method == 'GET':
        topic.click += 1
        db.session.commit()
        return render_template('voice/topic.html', title=gettext('Topic'),
                               topic=topic,
                               comments=live_comments,
                               pagination=pagination)
    #save the comments and update the topic view page
    elif request.method == 'POST':
        if not current_user.is_authenticated:
            abort(403)

        reply_content = request.form['content']

        if not reply_content or len(reply_content) > 140:
            message = gettext('Comment cannot be empty or too larger')
            return render_template('voice/topic.html',
                                   title=gettext('Topic'),
                                   message=message,
                                   topic=topic,
                                   comments=live_comments,
                                   pagination=pagination)

        topic.reply_count += 1;
        c = Comment(content=reply_content, user_id=current_user.uid, topic_id=tid)
        c.content_rendered = add_user_links_in_content(c.content_rendered)
        db.session.add(c)
        db.session.commit()

        topic.add_comment(c.id)
        current_user.add_comment(c.id)
        db.session.commit()

        #generate notify from the reply content
        add_notify_in_content(c.content,current_user.uid, tid, c.id)

        live_comments_all += [c]
        live_comments = live_comments_all[offset:offset+per_page]
        pagination = Pagination(page=page,total=len(live_comments_all),
                                per_page=per_page,
                                record_name='live_comments',
                                topic=topic,
                                comments=live_comments_all,
                                pagination=pagination
                    )

        return render_template('voice/topic.html', title=gettext('Topic'),
                               topic=topic,
                               comments=live_comments,
                               pagination=pagination)

    else:
        abort(404)