#!/usr/bin/python

from CoverTreeNN import CoverTreeNN
import unittest

def Distance1D(p, q):
  return abs(p - q)
  
def DepthFirstTraversal(node):
  if node.ephemeral:
    raise Exception('Found ephemeral node')
  messages = {(node.level, node.p,
               tuple(sorted(child.p for child in node._children)))}
  for child in node._children:
    messages.update(DepthFirstTraversal(child))
  return messages

class TestCoverTreeNN(unittest.TestCase):
  def setUp(self):
    self.nn = CoverTreeNN(Distance1D)
    for p in [5, 2, 0, 6, 0.5, 0.9]:
      self.nn.Insert(p)
      
  def testInsert(self):
    expected_nodes = {(3, 5, (0, 5)),
                      (2, 5, (2, 5)),
                      (2, 0, (0, )),
                      (1, 5, (5, )),
                      (1, 2, tuple()),
                      (1, 0, (0, )),
                      (0, 5, (5, 6)),
                      (0, 0, (0, 0.9)),
                      (-1, 5, tuple()),
                      (-1, 6, tuple()),
                      (-1, 0, (0, 0.5)),
                      (-1, 0.9, tuple()),
                      (-2, 0.5, tuple()),
                      (-2, 0, tuple())}
    nodes = DepthFirstTraversal(self.nn.root)
    self.assertEqual(expected_nodes, nodes)
    
  def testInsertRequiresEphemeralCleanup(self):
    nn = CoverTreeNN(Distance1D)
    for p in [5, 2, 3]:
      nn.Insert(p)

    expected_nodes = {(2, 5, (2, 5)),
                      (1, 5, tuple()),
                      (1, 2, (2, )),
                      (0, 2, (2, 3)),
                      (-1, 2, tuple()),
                      (-1, 3, tuple())}
    nodes = DepthFirstTraversal(nn.root)
    self.assertEqual(expected_nodes, nodes)
    
  def _TestFind(self, p, expected_q):
    dist, q = self.nn.Find(p)
    self.assertAlmostEqual(expected_q, q)
    
  def testFindNormalCase(self):
    self._TestFind(2.2, 2)
    
  def testFindNormalCaseWithChain(self):
    self._TestFind(0.8, 0.9)
    
  def testFindDistant(self):
    self._TestFind(100, 6)

if __name__ == '__main__':
  unittest.main()
