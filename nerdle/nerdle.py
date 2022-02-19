#!/usr/bin/env python

import itertools
import re
import sys
from collections import defaultdict

def complement(key):
  missing = [o for o in '+-*/' if o not in key]
  return { "".join(missing), "".join(reversed(missing)) }

def concrete(eqn, opKey):
  return (('%d %%s %d %%s %d = %d') % eqn) % (opKey[0], opKey[1])

def squeeze(t):
  for i in range(4):
    yield t[0:i] + (t[i]*10+t[i+1],) + t[i+2:]

ops = {
  '+-': lambda a, b, c, d: a + (b - c) == d,
  '-+': lambda a, b, c, d: (a - b) + c == d,
  '+*': lambda a, b, c, d: a + (b * c) == d,
  '*+': lambda a, b, c, d: (a * b) + c == d,
  '+/': lambda a, b, c, d: b == (d - a) * c,
  '/+': lambda a, b, c, d: a == (d - c) * b,
  '-*': lambda a, b, c, d: a - (b * c) == d,
  '*-': lambda a, b, c, d: (a * b) - c == d,
  '-/': lambda a, b, c, d: b == (a - d) * c,
  '/-': lambda a, b, c, d: a == (d + c) * b,
  '*/': lambda a, b, c, d: a * b == d * c,
  '/*': lambda a, b, c, d: a * c == d * b
}

results = defaultdict(lambda: defaultdict(set))
for digits in itertools.permutations(range(10), 5):
  key = frozenset(digits)
  for nums in squeeze(digits):
    for k, p in ops.items():
      if p(*nums):
        results[key][k].add(nums)

def parseEqn(eqn):
  if not re.match(r'^\d+[-+*/]\d+[-+*/]\d+=\d+$', re.sub(r'\s', '', eqn)):
    raise Exception('Invalid equation: ' + eqn)
  digits = frozenset(map(int, re.findall(r'\d', eqn)))
  numbers = tuple(map(int, re.findall(r'\d+', eqn)))
  ops = tuple(re.findall(r'[-+*/]', eqn))
  if len(digits) < 5:
    raise Exception('Invalid equation (not enough digits): ' + eqn)
  elif len(digits) > 5:
    raise Exception('Invalid equation (too many digits): ' + eqn)
  if len(set(digits)) != 5:
    raise Exception('Invalid equation (digits not unique): ' + eqn)
  if len(set(ops)) != 2:
    raise Exception('Invalid equation (operations not unique): ' + eqn)
  return (digits, concrete(numbers, ops))

if len(sys.argv) > 1:
  for (l, lc) in map(parseEqn, sys.argv[1:]):
    r = frozenset(range(10)) - l
    cvalid = [
      o for o in ops.keys()
      if (not (set(o) & set(lc))) and o in results[r]
    ]
    rs = [concrete(rc, v) for v in cvalid for rc in results[r][v]]
    print '   %s' % lc
    print '===%s===' % ('=' * len(lc))
    print '\n'.join('   ' + rr for rr in rs)
    print ''
  exit(0)

total = 0
for l in results:
  r = frozenset(range(10)) - l
  if 0 not in l or r not in results:
    continue
  fvalid = set(results[l]) & reduce(set.union, map(complement, results[r]), set())
  cvalid = reduce(set.union, map(complement, fvalid), set())
  if not fvalid:
    continue
  ls = [concrete(lc, v) for v in fvalid for lc in results[l][v]]
  rs = [concrete(rc, v) for v in cvalid for rc in results[r][v]]
  total += len(ls) + len(rs)
  blank = ["              "]
  ls += (len(rs) - len(ls)) * blank
  rs += (len(ls) - len(rs)) * blank
  print "-------------------------------"
  print "|  %s   |   %s  |" % (" ".join(map(str, sorted(l))), " ".join(map(str, sorted(r))))
  print "---------------+---------------"
  for z in zip(ls, rs):
    print "%14s | %s" % z
  print "-------------------------------"
  print ""

print "Total number of equations: %d" % total
