#!/usr/bin/env python

import argparse
import re
import string
import sys

from itertools import combinations_with_replacement, permutations, product

def nat(v):
  """
  Map a tuple of digits to the natural it represents.
  Ex: nat((1, 2, 3)) => 123, nat((0, 2, 4)) => 24
  """
  r = 0
  for d in v:
    r = r * 10 + d
  return r

def partition_int(n, r):
  """
  Generate the r-partitions of n
  Ex: partition_int(4, 2) => (1, 3), (2, 2), (3, 1)
  """
  if r == 0:
    yield tuple()
  elif r == 1:
    yield (n,)
  else:
    for i in range(1, (n+2)-r):
      for p in partition_int(n - i, r - 1):
        yield (i,) + p

def apply_int_partition(d, p, *stack):
  """
  Generate tuple of tuples described by the int-partition p drawing values from d.
  No stack should be given initially.
  Note that d is drawn with replacement, but only tuples covering all of d are generated.
  Ex: if d is {1, 2, 3} and p is (1, 2, 1) then this should yield items like
    ((1,), (2, 3), (1,)); and (note all digits used, and tuple(map(len, _)) == p)
    ((2,), (2, 3), (1,)); and
    ((1,), (1, 3), (2,)); ...
  """
  if p:
    for o in combinations_with_replacement(d, p[0]):
      for f in apply_int_partition(d, p[1:], o, *stack):
        yield f
  elif set(sum(stack, ())) == d:
    yield tuple(reversed(stack))

def partitions(d, r):
  """
  Generate r-tuple of tuples drawn from d (and covering all of d).
  Does not respect order, so if
    ((1,), (2, 3), (3,))
  is generated, then
    ((1,), (3, 2), (3,))
  will not be generated.
  Given that we know we want 8 items total (it's nerdle), we know how to invoke partition_int.
  Ex: if d is {1, 2, 3} and r is 3 then we can get:
    ((1,), (2, 3), (1,)); and (note all digits used, and tuple(map(len, _)) == p)
    ((2,), (2, 3), (1,)); and
    ((1,), (1,), (2,3)); ...
  """
  d = set(d)
  for p in partition_int(8-(r-1), r):
    for f in apply_int_partition(d, p):
      yield f

def partitions_permuted(d, r):
  """
  Generate r-tuple of tuples drawn from d (and covering all of d) respecting order.
  Ex: if d is {1, 2, 3} and r is 3 then we can get:
    ((1,), (2, 3), (1,)); and (note all digits used, and tuple(map(len, _)) == p)
    ((1,), (3, 2), (1,)); and
    ((2,), (2, 3), (1,)); and
    ((2,), (3, 2), (1,)); and
    ((1,), (1,), (2,3)); and
    ((1,), (1,), (3,2)); ...
  """
  for p in partitions(d, r):
    for item in product(*map(permutations, p)):
      yield item

def filter_lengths(seq, filters):
  """
  Generate items drawn from seq where the i'th item has the requested length.
  filters should be a dict from indices to acceptable lengths (checked w/ 'in').
  For example we could have
    filter_lengths(seq, {2: [3], 1: [2, 3]})
  to require the third item has length 3 and the second has length 2 or 3.
  """
  for (i, r) in filters.items():
    seq = (s for s in seq if len(s[i]) in r)
  for s in seq:
    yield s

# Predicates based on sole operator or first and second operator.
# Returns true if the given values produce a valid equation.
operation_predicates = {
  '+': lambda l, r, o: l + r == o,
  '-': lambda l, r, o: l - r == o,
  '*': lambda l, r, o: l * r == o,
  '/': lambda l, r, o: l == o * r,

  '++': lambda l, m, r, o: l + m + r == o,
  '+-': lambda l, m, r, o: l + m - r == o,
  '-+': lambda l, m, r, o: l - m + r == o,
  '--': lambda l, m, r, o: l - m - r == o,

  '**': lambda l, m, r, o: l * m * r == o,
  '*/': lambda l, m, r, o: l * m == o * r,
  '/*': lambda l, m, r, o: l * r == o * m,
  '//': lambda l, m, r, o: l == o * m * r,

  '+*': lambda l, m, r, o: l + m * r == o,
  '*+': lambda l, m, r, o: l * m + r == o,
  '-*': lambda l, m, r, o: l - m * r == o,
  '*-': lambda l, m, r, o: l * m - r == o,

  '+/': lambda l, m, r, o: m == (o - l) * r,
  '/+': lambda l, m, r, o: l == (o - r) * m,
  '-/': lambda l, m, r, o: m == (l - o) * r,
  '/-': lambda l, m, r, o: l == (o + r) * m
}

def filter_operations(seq, *ops):
  """
  Return dict keyed by ops of items in seq that result in valid equation for the given op.
  Seq should be tuple of tuples, so something like ((1, 2), (3, 4), (5, 6)) which would be
  mapped to (12, 34, 56) and then checked with the given op for correctnest.
  Ops are keys to operation_predicates (see above).
  """
  results = {op: [] for op in ops}
  for s in seq:
    v = map(nat, s)
    for op in ops:
      if operation_predicates[op](*v):
        results[op].append(s)
  return results

def compile_working(working):
  """
  Generate string of equations for op to eq-list dict of working equations.
  Ex:
    compile_working({'+': [((1, 2), (3, 4), (4, 6))]})
  would generate
    '12+34=46'
  """
  for op, candidates in working.items():
    for c in candidates:
      n = tuple(''.join(map(str, t)) for t in c)
      f = '%%s'.join('%s' for _ in n)
      yield (f % n) % tuple(op + '=')

def grep_working(working, selects, rejects):
  """
  Generate criteria-matching equations from op to eq-list dict of working equations.
  Selects and rejects should be dicts of positions to sequences of (un)acceptable characters.
  """
  for eq in compile_working(working):
    if not all(eq[pos] in sel for pos, sel in selects.items()):
      continue
    if any(eq[pos] in rej for pos, rej in rejects.items()):
      continue
    yield eq

def generate(digits, ops, permuteOps, lengths, selects, rejects):
  """
  Generates the working equations matching the constraint criteria.
  - digits: the digits to draw the equation from, i.e. [1, 2, 3, 4, 6];
  - ops: string of ops to draw equation from, i.e. '*' or '+*';
  - permuteOps: if len(ops) is 2 then consider its reverse if true;
  - lengths: dict of number indices to acceptable characters.
  - selects: dict of positions to a string of acceptable characters.
  - rejects: dict of positions to a string of unacceptable characters.
  Ex:
    generate([1, 2, 3, 4, 6], '*', False, {2: [3]}, {4: '='}, {0: '12', 7: ['2', '3']})
  """
  permuted = partitions_permuted(digits, 2 + len(ops))
  lengthed = filter_lengths(permuted, lengths)
  ops_filter = set([ops, ops[::-1]]) if permuteOps else [ops]
  working = filter_operations(lengthed, *ops_filter)
  return list(grep_working(working, selects, rejects))

def decimal_digit(d):
  if d in string.digits and len(d) == 1:
    return int(d)
  err = 'Invalid digit ' + d + ' -- must be given single digits for positional arguments.'
  raise argparse.ArgumentTypeError(err)

def parse_indexed_pair(s, name, pattern, display_format, rmap=None):
  if not re.match(pattern, s):
    err = 'Invalid %s, must be %s.' % (name, display_format)
    raise argparse.ArgumentTypeError(err)
  left, right = s.split(':')
  if len(left) != len(right):
    lname, rname = display_format.split(':')
    err = 'Invalid %s, must have as many %s as %s.' % (name, lname, rname)
    raise argparse.ArgumentTypeError(err)
  left, right = map(int, left), map(rmap or (lambda k: k), right)
  left = map(lambda l: l - 1, left)
  result = {l: [] for l in left}
  for (l, r) in zip(left, right):
    result[l].append(r)
  return result

def num_length(s):
  return parse_indexed_pair(s, 'length', '[1-4]+:[1-4]+$', 'INDICES:LENGTHS', int)

def search_pattern(p):
  return parse_indexed_pair(p, 'selection/rejection pattern', '[1-8]+:[-+*/=0-9]+$', 'POSITIONS:CHARACTERS')

parser = argparse.ArgumentParser(description='Solving nerdle constraints.')
parser.add_argument(
  'digits',
  type=decimal_digit,
  nargs='+',
  help='Digits to use in solution (all will be used, replacement allowed).'
)
parser.add_argument(
  '--op1',
  choices=list('+-*/'),
  required=True,
  help='First operation to consider.'
)
parser.add_argument(
  '--op2',
  choices=list('+-*/'),
  required=False,
  help='Optional second operation to consider.'
)
parser.add_argument(
  '--unordered',
  action='store_true',
  help='Consider op2 as the first operation.'
)
parser.add_argument(
  '--length',
  type=num_length,
  metavar='INDICES:LENGTHS',
  help='Required length for a number. Indices are 1-4 and lengths are 1-4. \'114:123\' means the first number can be 1 or 2 digits and the third number must be 3 digits.'
)
parser.add_argument(
  '--select',
  type=search_pattern,
  metavar='POSITIONS:CHARACTERS',
  help='Select equations with characters at the given positions. e.g. \'2234:1+9=\' demands either 1 or + in the second position, 9 in the third position, and = in the fourth position.'
)
parser.add_argument(
  '--reject',
  type=search_pattern,
  metavar='POSITIONS:CHARACTERS',
  help='Reject equations with characters at the given positions. e.g. \'2234:1+9=\' rejects either 1 or + in the second position, 9 in the third position, and = in the fourth position.'
)

args = parser.parse_args()
if len(args.digits) > 6:
  parser.error('Too many digits given.')
if len(args.digits) == 6 and args.op2:
  parser.error('Too many digits for two operations.')
if 3 in (args.length or {}) and not args.op2:
  parser.error('Length index out of range without second operation.')

results = generate(
  args.digits,
  args.op1 + (args.op2 or ''),
  args.unordered,
  args.length or {},
  args.select or {},
  args.reject or {}
)

def format_result(r):
  pat = re.compile('([-+*/=])')
  return re.sub(pat, r' \1 ', r, count=3)

output = '\n'.join(sorted(map(format_result, results)))
if output:
  print output
