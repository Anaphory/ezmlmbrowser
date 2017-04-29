from pyramid.view import view_config

import os

from .ezmlm import List


with open("path") as paths:
    for path in paths:
        lists = {dir: List(dir, path.strip())
                 for dir in os.listdir(path.strip())}


@view_config(route_name="lists", renderer="templates/lists.jinja2")
def lists_view(request):
    """Show all mailing lists."""
    return {"project": "ezmlmbrowser",
            "lists": lists.values()}


@view_config(route_name="list", renderer="templates/list.jinja2")
def list_view(request):
    archive = request.matchdict['list']
    return {"list": lists[archive]}


@view_config(route_name="threads", renderer="templates/threads.jinja2")
def threads_view(request):
    archive = request.matchdict['list']
    year = int(request.matchdict['year'])
    month = int(request.matchdict['month'])
    return {"list": lists[archive],
            "year": year,
            "month": month,
            "threads": lists[archive].by_date(year, month)}


@view_config(route_name="author", renderer="templates/thread.jinja2")
def author_view(request):
    archive = request.matchdict['list']
    author = request.matchdict['author']
    return {"list": lists[archive],
            "thread": lists[archive].by_author(author)}


@view_config(route_name="thread", renderer="templates/thread.jinja2")
def thread_view(request):
    archive = request.matchdict['list']
    thread = request.matchdict['thread']
    return {"list": lists[archive],
            "thread": lists[archive].by_thread(thread)}


@view_config(route_name="message", renderer="templates/message.jinja2")
def message_view(request):
    archive = request.matchdict['list']
    message = int(request.matchdict['messageid'])
    thread = lists[archive].thread_for_message(message)
    return {"list": lists[archive],
            "number": message,
            "thread": lists[archive].by_thread(thread),
            "message": lists[archive].by_number(message)}
