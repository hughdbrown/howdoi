#!/usr/bin/env python
# -*- coding: utf-8 -*-

##################################################
#
# howdoi - a code search tool.
# written by Benjamin Gleitzman (gleitz@mit.edu)
# inspired by Rich Jones (rich@anomos.info)
#
##################################################

from urllib import quote
import argparse
import re

from pyquery import PyQuery as pq
import requests
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import TerminalFormatter


SITE_SUFFIX = "q=site:stackoverflow.com%20{0}"
GOOGLE_SEARCH_URL = "https://www.google.com/search?" + SITE_SUFFIX
DUCK_SEARCH_URL = "http://duckduckgo.com/html?" + SITE_SUFFIX
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17"

def get_result(url):
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    return r.text

def is_question(link):
    return re.search(r'questions/\d+/', link)

def get_google_links(query):
    url = GOOGLE_SEARCH_URL.format(quote(query))
    result = get_result(url)
    html = pq(result)
    return [a.attrib['href'] for a in html('.l')]

#def get_duck_links(query):
#    url = DUCK_SEARCH_URL.format(quote(query))
#    result = get_result(url)
#    html = pq(result)
#    links = [l.find('a').attrib['href'] for l in html('.links_main')]
#    return links

def get_link_at_pos(links, pos):
    questions = [link for link in links if is_question(link)]
    pos = min(int(pos), len(questions))
    return questions[pos - 1]

def get_instructions(args):
    links = get_google_links(args['query'])
    if not links:
        return ''

    link = get_link_at_pos(links, args['pos'])
    if args.get('link'):
        return link

    link = link + '?answertab=votes'
    page = get_result(link)
    html = pq(page)
    first_answer = html('.answer').eq(0)
    instructions = first_answer.find('pre') or first_answer.find('code')
    if args['all'] or not instructions:
        text = first_answer.find('.post-text').eq(0).text()
    else:
        text = instructions.eq(0).text()
    return text or ''

def howdoi(args):
    args['query'] = ' '.join(args['query']).replace('?', '')
    instructions = get_instructions(args) or "Sorry, could not find any help with that topic"
    print highlight(
        instructions,
        guess_lexer(instructions),
        TerminalFormatter(bg='dark')
    )

def command_line_runner():
    parser = argparse.ArgumentParser(description='code search tool')
    parser.add_argument('query', metavar='QUERY', type=str, nargs=argparse.REMAINDER,
                        help='the question to answer')
    parser.add_argument('-p','--pos', help='select answer in specified position (default: 1)', default=1)
    parser.add_argument('-a','--all', help='display the full text of the answer',
                        action='store_true')
    parser.add_argument('-l','--link', help='display only the answer link',
                        action='store_true')
    args = vars(parser.parse_args())
    howdoi(args)

if __name__ == '__main__':
    command_line_runner()
