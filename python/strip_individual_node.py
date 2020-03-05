#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


def strip_node(node):
    ''' Strip the node and keep its text and tail textual content. Source:
        https://stackoverflow.com/questions/21685795/
        using-python-and-lxml-to-strip-only-the-tags-that-have-certain-attributes-values#21686786
        NB: I'm not using this because
        etree.strip_tags(tree, 'z')
        and
        etree.strip_elements(tree, 'y', with_tail=False)
        do a great job already, but I'm keeping it for future reference.
        '''
    text_content = node.xpath('string()')

    # Include tail in full_text because it will be removed with the node
    full_text = text_content + (node.tail or '')

    parent = node.getparent()
    prev = node.getprevious()
    if prev:
        # There is a previous node, append text to its tail
        prev.tail += full_text
    else:
        # It's the first node in <parent/>, append to parent's text
        parent.text = (parent.text or '') + full_text
    parent.remove(node)
