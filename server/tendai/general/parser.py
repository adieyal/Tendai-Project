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
            return cls(head)    
        except IOError, e:
            print 'Error parsing submission: %s' % (e)
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
    
    def __iter__(self):
        self._current_node = 0
        return self
    
    def next(self):
        if self._current_node == len(self.head.childNodes):
            raise StopIteration
        next_node = self.head.childNodes[self._current_node]
        self._current_node += 1
        if len(next_node.childNodes) == 0:
            return None
        if len(next_node.childNodes) == 1:
            child = next_node.firstChild
            if child.nodeType == child.TEXT_NODE:
                return child.data
        return self.__class__(next_node)
    
    def __repr__(self):
        return u'Parser: %s' % (self.head.nodeName)
    
    def name(self):
        return u'%s' % (self.head.nodeName)

