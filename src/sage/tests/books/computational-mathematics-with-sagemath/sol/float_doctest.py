# sage_setup: distribution = sagemath-repl
"""
This file (./sol/float_doctest.sage) was *autogenerated* from ./sol/float.tex,
with sagetex.sty version 2011/05/27 v2.3.1.
It contains the contents of all the sageexample environments from this file.
You should be able to doctest this file with:
sage -t ./sol/float_doctest.sage
It is always safe to delete this file; it is not used in typesetting your
document.

Sage example in ./sol/float.tex, line 17::

  sage: R100=RealField(100)
  sage: x=R100(10^30)
  sage: x>2^99
  True
  sage: x<2^100
  True

Sage example in ./sol/float.tex, line 48::

  sage: e=2^100
  sage: s1=10^30
  sage: significand=[]
  sage: nbdigits=0 # number of significant digits
  sage: while s1>0:
  ....:    e/=2
  ....:    if e<=s1:
  ....:        significand.append(1)
  ....:        s1-=e
  ....:    else:
  ....:        significand.append(0)
  ....:    nbdigits+=1
  sage: print(significand)
  [1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0,
   1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
   0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1,
   1, 1, 1, 0, 1, 0, 1, 0, 0, 1]
  sage: print("number of significant digits: " + str(nbdigits))
  number of significant digits: 70

Sage example in ./sol/float.tex, line 86::

  sage: R100=RealField(100)
  sage: x=R100(10^30)
  sage: s,m,e = x.sign_mantissa_exponent()
  sage: s,m,e
  (1, 1000000000000000000000000000000, 0)

Sage example in ./sol/float.tex, line 126::

  sage: var("u0 u1 u2 alpha beta gamma n")
  (u0, u1, u2, alpha, beta, gamma, n)
  sage: recurrence = lambda a,b:  111-1130/a+3000/(a*b)
  sage: gener1 = lambda n: (alpha*100^n+beta*6^n+gamma*5^n)
  sage: solGen =  lambda n: gener1(n+1)/gener1(n)

Sage example in ./sol/float.tex, line 137::

  sage: u2 = recurrence(u1,u0)
  sage: s = [u2==solGen(2),u1==solGen(1),u0==solGen(0)]
  sage: t = [s[i].substitute(u0=2,u1=-4) for i in range(0,3)]

Sage example in ./sol/float.tex, line 143::

  sage: solve(t,alpha,beta,gamma)
  [[alpha == 0, beta == -3/4*r1, gamma == r1]]

Sage example in ./sol/float.tex, line 157::

  sage: alpha=0
  sage: beta = -3/4*gamma
  sage: final=solGen(n)-recurrence(solGen(n-1),solGen(n-2))
  sage: final.simplify_full()
  0

Sage example in ./sol/float.tex, line 179::

  sage: def recur(x1,x0):
  ....:     return 111 - 1130/x1 + 3000/(x0*x1)

Sage example in ./sol/float.tex, line 190::

  sage: u0 = 2.
  sage: u1 = -4.
  sage: for i in range(1,25):
  ....:     x = recur(u1,u0)
  ....:     print((i, x))
  ....:     u0 = u1
  ....:     u1 = x
  (1, 18.5000000000000)
  (2, 9.37837837837838)
  (3, 7.80115273775217)
  (4, 7.15441448097533)
  (5, 6.80678473692481)
  (6, 6.59263276872179)
  ..................
  (23, 99.9999986592167)
  (24, 99.9999999193218)

Sage example in ./sol/float.tex, line 229::

  sage: var("x")
  x
  sage: solve(x==recurrence(x,x),x)
  [x == 100, x == 5, x == 6]

Sage example in ./sol/float.tex, line 256::

  sage: RL = RealField(5000)
  sage: u0 = RL(2)
  sage: u1 = RL(-4)
  sage: for i in range(1,2500):
  ....:     x = recur(u1,u0)
  ....:     u0 = u1
  ....:     u1= x
  sage: x
  100.00000000000000000000000000000000000000000000000000000...

Sage example in ./sol/float.tex, line 281::

  sage: u0 = 2
  sage: u1 = -4
  sage: for i in range(1,2500):
  ....:     x = recur(u1,u0)
  ....:     u0 = u1
  ....:     u1 = x
  sage: float(x)
  6.0

Sage example in ./sol/float.tex, line 325::

  sage: f = lambda x: x^2
  sage: g = lambda x: x*x
  sage: sage.rings.real_mpfi.printing_style = 'brackets'
  sage: I = RIF(-1,1)
  sage: f(I)
  [0.0000000000000000 .. 1.0000000000000000]
  sage: g(I)
  [-1.0000000000000000 .. 1.0000000000000000]

"""
