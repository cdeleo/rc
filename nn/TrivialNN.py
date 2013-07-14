#!/usr/bin/python

class TrivialNN(object):
  def __init__(self, dist):
    self.points = []
    self.dist = dist

  def Add(self, p):
    self.points.append(p)

  def Find(self, p):
    min_dist, min_point = min((self.dist(p, q), q)
                              for q in self.points)
    return (min_dist, min_point)
