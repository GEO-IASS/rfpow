# -*- coding: utf-8 -*-
import re

"""
Various handy filters for Jinja

Borrowed from: http://www.koders.com/python/fid193CE4F072A4BEF0222C0758A7FF4BDAFF3FC8DF.aspx?s=search#L475
(which I don't think is the original source)

"""

def do_nl2pbr(s):
    """
    {{ s|nl2pbr }}

    Convert newlines into <p> and <br />s.
    """
    if not isinstance(s, basestring):
        s = str(s)
    s = re.sub(r'\r\n|\r|\n', '\n', s)
    paragraphs = re.split('\n{2,}', s)
    paragraphs = ['<p>%s</p>' % p.strip().replace('\n', '<br />') for p in paragraphs]
    return '\n\n'.join(paragraphs)
