#!/usr/bin/python

# Implemented from Cover Trees for Nearest Neighbor, Beygelzimer et al.

import math
import weakref

class Node(object):
  def __init__(self, p, level, parent=None):
    self.p = p
    self.level = level
    self.ephemeral = False
    self._children = []
    if parent:
      self._parent = weakref.ref(parent)
    else:
      self._parent = None
    
  def CreateChild(self, p):
    if not self._children:
      # If there are any explicit children, the self-child must be one
      self._children.append(Node(self.p, self.level - 1, self))
    elif len(self._children) == 1:
      # Adding a sibling for an ephemeral node makes it explicit
      self._children[0].ephemeral = False
    self._children.append(Node(p, self.level - 1, self))
    
  def CreateParent(self):
    parent = Node(self.p, self.level + 1)
    parent._children.append(self)
    self._parent = weakref.ref(parent)
    return parent
    
  def IsValidParent(self, p, dist):
    return dist(p, self.p) <= 2 ** self.level
    
  def Children(self, createephemeral):
    if not self._children and createephemeral:
      self._children.append(Node(self.p, self.level - 1, self))
      self._children[-1].ephemeral = True
    return self._children
    
  def Cleanup(self):
    if self.ephemeral:
      if not self._children:
        # Remove self
        parent = self._parent() if self._parent else None
        if parent:
          parent._children.remove(self)
      else:
        self.ephemeral = False
    
  def __repr__(self):
    ephemeral_status = ' (ephemeral)' if self.ephemeral else ''
    return '<Node level=%d value=%s%s>' % (self.level, self.p,
                                           ephemeral_status)

class CoverTreeNN(object):
  def __init__(self, dist):
    self.root = None
    self.dist = dist
    
  def _InsertInner(self, p, Q, ephemeral_nodes):
    valid_parents = [q for q in Q if q.IsValidParent(p, self.dist)]
    if valid_parents:
      children_to_explore = []
      for parent in valid_parents:
        new_children = parent.Children(True)
        if len(new_children) == 1 and new_children[0].ephemeral:
          # Track created ephemeral nodes
          ephemeral_nodes.append(new_children[0])
        children_to_explore.extend(new_children)
        
      if not self._InsertInner(p, children_to_explore, ephemeral_nodes):
        # This is the minimum level with valid parents, so insert
        valid_parents[0].CreateChild(p)
      return True
    else:
      # This is too low in the tree to insert p
      return False

  def Insert(self, p):
    if not self.root:
      # First node in the tree
      self.root = Node(p, None)
    else:
      d = self.dist(p, self.root.p)
      min_level = int(math.ceil(math.log(d) / math.log(2)))
      if self.root.level is None:
        # Second node in the tree
        # Pins down the starting root level
        self.root.level = min_level
        self.root.CreateChild(p)
      else:  
        if min_level > self.root.level:
          # New node requires the explicit root to move up
          for level in xrange(self.root.level, min_level):
            self.root = self.root.CreateParent()
            
        # Normal-case insertion
        ephemeral_nodes = []
        self._InsertInner(p, [self.root], ephemeral_nodes)
        while ephemeral_nodes:
          ephemeral_nodes.pop().Cleanup()
        
  def Find(self, p):
    nodes_to_explore = [self.root]
    global_min = None
    while nodes_to_explore:
      child_nodes = []
      for node in nodes_to_explore:
        child_nodes.extend(node.Children(False))
      nodes_to_explore = []
      if child_nodes:
        child_dists = [(self.dist(p, child.p), child)
                       for child in child_nodes]
        min_dist, min_child = min(child_dists)
        if not global_min or min_dist < global_min[0]:
          global_min = (min_dist, min_child.p)
        for child_dist, child in child_dists:
          if child_dist - 2 ** (child.level + 1) < min_dist:
            nodes_to_explore.append(child)
    return global_min
