# -*- coding: utf-8 -*-
"""Extend pygraphml with tags and attributes that can be read by yEd.

This allows to use yEd to show and create pygraphml data.
https://www.yworks.com/products/yed
"""
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import ast
from xml.dom import minidom

from . import Graph
from . import Node
from . import Edge
__all__ = ['GraphMLYedParser']


class GraphMLYedParser(object):

    """Write and Read graphml files for and from yEd.

    This allows to include more information to your graphs.
    So far, different shapes, colors, and geometry are supported.
    """

    # The supported yEd tags and their value schema
    yed_tags = {'y:ShapeNode': {},
                'y:NodeLabel': '',
                'y:Geometry': {
                    'height': '30.0',
                    'width': '30.0',
                    'x': '0.0',
                    'y': '0.0'
                    },
                'y:Fill': {
                    'color': '#FFFFFF'
                    },
                'y:Shape': {
                    'type': 'rectangle'
                    }
                }

    def write(self, graph, fname):
        """Write the graph with the yEd information.

        Args:
            graph (Graph): The graph
            fname (str): The file path
        """
        doc = self.graph_to_xml(graph)
        f = open(fname, 'w')
        f.write(doc.toprettyxml(indent='    '))
    # end def write

    def graph_to_xml(self, graph):
        """Convert the given Graph to xml.

        Args:
            graph (Graph): The Graph
        Returns:
            The xml document
        """
        doc = minidom.parseString('<graphml xmlns="http://graphml.graphdrawing.org/xmlns" '
                                  'xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" '
                                  'xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" '
                                  'xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" '
                                  'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                                  'xmlns:y="http://www.yworks.com/xml/graphml" '
                                  'xmlns:yed="http://www.yworks.com/xml/yed/3" '
                                  'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">'
                                  '</graphml>')
        root = doc.firstChild
        nodegraphics = minidom.parseString('<key for="node" id="d6" yfiles.type="nodegraphics"/>').firstChild
        root.appendChild(nodegraphics)

        # Add attributs
        for a in graph.get_attributs():
            if a.name not in self.yed_tags.keys():
                attr_node = doc.createElement('key')
                attr_node.setAttribute('id', a.name)
                attr_node.setAttribute('attr.name', a.name)
                attr_node.setAttribute('attr.type', a.type)
                root.appendChild(attr_node)
            # end if
        # end for

        graph_node = doc.createElement('graph')
        graph_node.setAttribute('id', graph.name)
        if graph.directed:
            graph_node.setAttribute('edgedefault', 'directed')
        else:
            graph_node.setAttribute('edgedefault', 'undirected')
        # end if
        root.appendChild(graph_node)

        # Add nodes
        for n in graph.nodes():
            node = doc.createElement('node')
            node.setAttribute('id', n['label'])
            self.create_yed_node(doc, n, node)
            graph_node.appendChild(node)
        # end for

        # Add edges
        for e in graph.edges():
            edge = doc.createElement('edge')
            edge.setAttribute('source', e.node1['label'])
            edge.setAttribute('target', e.node2['label'])
            if e.directed() != graph.directed:
                edge.setAttribute('directed', 'true' if e.directed() else 'false')
            # end if
            for a in e.attributes():
                if e != 'label':
                    data = doc.createElement('data')
                    data.setAttribute('key', a)
                    data.appendChild(doc.createTextNode(e[a]))
                    edge.appendChild(data)
                # end if
            # end if
            graph_node.appendChild(edge)
        # end for
        return doc
    # end def graph_to_xml

    def create_yed_node(self, doc, graph_node, node):
        """Add tags and attributes readable by yEd.

        Args:
            doc (minidom.Document): The minidom Document
            graph_node (Node): The Node
            node (minidom.Element): The xml Element
        """
        data = doc.createElement('data')
        data.setAttribute('key', 'd6')
        ShapeNode = doc.createElementNS('y', 'y:ShapeNode')
        data.appendChild(ShapeNode)
        node.appendChild(data)

        # Additional attributes
        for attr in graph_node.attributes():
            if attr == 'label':
                continue
            # end if
            attr_node = doc.createElementNS('y', format(attr))
            try:
                for key, value in ast.literal_eval(graph_node[attr]).items():
                    attr_node.setAttribute(key, value)
                # end for
            except:
                attr_node.appendChild(doc.createTextNode(graph_node[attr]))
            # end try
            ShapeNode.appendChild(attr_node)
        # end for
    # end def create_yed_node

    def parse(self, fname):
        """Convert the given graphml file to a graph.

        Takes the yEd information into account.
        """
        with open(fname, 'r') as f:
            graph = self.xml_to_graph(f.read())
        # end with
        return graph
    # end def parse

    def xml_to_graph(self, graphml_string):
        """Convert the given xml string to a Graph.

        Args:
            graphml_string (str): A graphml xml string
        Returns:
            The Graph
        """
        dom = minidom.parseString(graphml_string)
        root = dom.getElementsByTagName('graphml')[0]
        xml_graph = root.getElementsByTagName('graph')[0]
        name = xml_graph.getAttribute('id')

        graph = Graph(name)

        # Get nodes
        for node in xml_graph.getElementsByTagName('node'):
            n = graph.add_node(node.getAttribute('id'))

            for attr in node.getElementsByTagName('data'):
                self.parse_yed_node(attr, n)
            # end for
        # end for

        # Get edges
        for edge in xml_graph.getElementsByTagName('edge'):
            source = edge.getAttribute('source')
            dest = edge.getAttribute('target')
            e = graph.add_edge_by_label(source, dest)

            for attr in edge.getElementsByTagName('data'):
                if attr.firstChild:
                    e[attr.getAttribute('key')] = attr.firstChild.data
                else:
                    e[attr.getAttribute('key')] = ''
                # end if
            # end for
        # end for

        return graph
    # end def xml_to_graph

    def parse_yed_node(self, element, node):
        """Parse the given Element for yEd ShapeNodes and attributes.

        Args:
            element (minidom.Element): The Element
            node (Node): The node
        """
        for c in element.childNodes:
            if c.localName == 'ShapeNode':
                for c2 in c.childNodes:
                    if c2.localName == 'NodeLabel':
                        node['y:NodeLabel'] = c2.firstChild.data
                    elif c2.localName == 'Fill':
                        node['y:Fill'] = {str('color'): str(c2.attributes['color'].value)}
                    elif c2.localName == 'Geometry':
                        geometry = dict()
                        for attr in c2.attributes.keys():
                            geometry[str(attr)] = str(c2.attributes[attr].value)
                        # end for
                        node['y:Geometry'] = geometry
                    elif c2.localName == 'Shape':
                        node['y:Shape'] = {str('type'): str(c2.attributes['type'].value)}
                    # end if
                # end for
            # end if
        # end for
    # end def parse_yed_node
# end class GraphMLYedParser
