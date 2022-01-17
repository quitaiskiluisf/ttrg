#! /usr/bin/env python3

def xml_first_child_or_error(xml_fragment, tag=None):
    ''' In an XML fragment, locates the first child node whose tag name is equal to the supplied tag name.
        If no tag name is supplied, returns the first child node. If a name is supplied but there's no tag
        with that name, generates an error message. '''

    if xml_fragment.nodeType == xml_fragment.DOCUMENT_NODE:
        if xml_fragment.documentElement.tagName == tag:
            return xml_fragment.documentElement

        raise Exception(f'Found tag "{xml_fragment.documentElement.tagName}" as the root element. Expected "{tag}" tag.')
    else:
        for child in xml_fragment.childNodes:
            # skips objects which are not ELEMENT_NODE (comments, breaks, etc.)
            if child.nodeType != xml_fragment.ELEMENT_NODE:
                continue
            if tag == None or child.tagName == tag:
                return child
        raise Exception(f'Element "{xml_fragment.tagName}" does not have any element "{tag}" as a child node.')


def xml_set_node_value(xml_node, value):
    ''' If the given node already contains a TextNode, replace its content with the new value;
        if it does not contain a TextNode, create one and add to it with the new value. '''
    if xml_node.firstChild != None:
        xml_node.firstChild.nodeValue = value
    else:
        n = xml_node.ownerDocument.createTextNode(value)
        xml_node.appendChild(n)
