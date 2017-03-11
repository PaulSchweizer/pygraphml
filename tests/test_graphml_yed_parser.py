import os
import sys

import unittest
import mock

sys.path.insert(0, 'C:\PROJECTS\DungeonCrawler\python\pygraphml')

from pygraphml.praphml_yed_parser import GraphMLYedParser
from pygraphml import Graph


class TestGraphMLYedParser(unittest.TestCase):

    """Test the GraphMLYedParser."""

    def test_write_graph(self):
        """Create a graph, convert it to xml, parse it and compare."""
        graph1 = Graph()

        node0 = graph1.add_node('0')
        node0['y:NodeLabel'] = 'Node0'
        node0['y:Fill'] = {'color': '#FF9999'}
        node0['y:Shape'] = {'type': 'ellipse'}
        node0['y:Geometry'] = {'width': '100'}

        node1 = graph1.add_node('1')
        node1['y:NodeLabel'] = 'Node1'
        node1['y:Fill'] = {'color': '#99FF99'}
        node1['y:Shape'] = {'type': 'rectangle'}
        node1['y:Geometry'] = {'width': '100'}

        node2 = graph1.add_node('3')
        node2['y:NodeLabel'] = 'Node2'
        node2['y:Fill'] = {'color': '#9999FF'}
        node2['y:Shape'] = {'type': 'diamond'}
        node2['y:Geometry'] = {'width': '100'}

        graph1.add_edge(node0, node1)
        graph1.add_edge(node0, node2)
        graph1.add_edge(node1, node2)

        # Convert to XML
        parser = GraphMLYedParser()
        xml = parser.graph_to_xml(graph1).toprettyxml(indent='    ')

        # Convert back to a graph and compare the two
        graph2 = parser.xml_to_graph(xml)

        for n1, n2 in zip(graph1.nodes(), graph2.nodes()):
            self.assertEqual(len(n1.attributes()), len(n2.attributes()))
            for attr in n1.attributes():
                self.assertEqual(n1[attr], n2[attr])
            # end for
        # end for

        for e1, e2 in zip(graph1.edges(), graph2.edges()):
            self.assertEqual(e1.node1['label'], e2.node1['label'])
            self.assertEqual(e1.node2['label'], e2.node2['label'])
        # end for
    # end def test_write_graph
# end class TestGraphMLYedParser


if __name__ == '__main__':
    unittest.main()
# end if
