from xml.dom import minidom

class XMLError(ValueError):
    pass

class SubmissionParser(object):
    def __init__(self, head=None):
        self.head = head

    @classmethod
    def from_file(cls, filename):
        try:
            dom = minidom.parse(filename)
            if len(dom.childNodes) != 1:
                raise XMLError('Expected single root node.')
            head = dom.firstChild
            if head.nodeName != 'data':
                raise XMLError('Expected root node name to be "data".')
            return cls(head)    
        except IOError:
            return None
    
    def children(self):
        children = []
        for node in self.head.childNodes:
            if len(node.childNodes) == 0:
                children.append(None)
            elif len(node.childNodes) == 1:
                child = node.firstChild
                if child.nodeType == child.TEXT_NODE:
                    children.append(child.data)
            else:
                children.append(self.__class__(node))
        return children
    
    def nodes(self):
        nodes = []
        for node in self.head.childNodes:
            nodes.append(node.nodeName)
        return nodes
    
    def __getattr__(self, attr):
        new_head = None
        for node in self.head.childNodes:
            if node.nodeName == str(attr):
                new_head = node
                break
        if not new_head:
            raise AttributeError('Node does not exist.')
        if len(new_head.childNodes) == 0:
            return None
        if len(new_head.childNodes) == 1:
            child = new_head.firstChild
            if child.nodeType == child.TEXT_NODE:
                return child.data
        return self.__class__(new_head)
    
    def __repr__(self):
        return 'Parser: %s' % (self.head.nodeName)

