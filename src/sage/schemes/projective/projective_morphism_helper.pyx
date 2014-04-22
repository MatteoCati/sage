r"""
Projective `n` space over a ring

EXAMPLES: We construct projective space over various rings of
various dimensions.

The simplest projective space::

    sage: ProjectiveSpace(0)
    Projective Space of dimension 0 over Integer Ring

A slightly bigger projective space over `\QQ`::

    sage: X = ProjectiveSpace(1000, QQ); X
    Projective Space of dimension 1000 over Rational Field
    sage: X.dimension()
    1000

We can use "over" notation to create projective spaces over various
base rings.

::

    sage: X = ProjectiveSpace(5)/QQ; X
    Projective Space of dimension 5 over Rational Field
    sage: X/CC
    Projective Space of dimension 5 over Complex Field with 53 bits of precision

The third argument specifies the printing names of the generators
of the homogenous coordinate ring. Using objgens() you can obtain
both the space and the generators as ready to use variables.

::

    sage: P2, (x,y,z) = ProjectiveSpace(2, QQ, 'xyz').objgens()
    sage: P2
    Projective Space of dimension 2 over Rational Field
    sage: x.parent()
    Multivariate Polynomial Ring in x, y, z over Rational Field

For example, we use `x,y,z` to define the intersection of
two lines.

::

    sage: V = P2.subscheme([x+y+z, x+y-z]); V
    Closed subscheme of Projective Space of dimension 2 over Rational Field defined by:
     x + y + z,
     x + y - z
    sage: V.dimension()
    0

AUTHORS:
 
- Dillon Rose (2014-01):  Speed enhancements

"""

#*****************************************************************************
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.rings.arith              import lcm
from sage.rings.finite_rings.constructor import GF, is_PrimeFiniteField
from sage.sets.all                 import Set

def _fast_possible_periods(self,return_points=False):
    r"""
    Returns the list of possible minimal periods of a periodic point
    over `\QQ` and (optionally) a point in each cycle.

    ALGORITHM:

    The list comes from: Hutz, Good reduction of periodic points, Illinois Journal of
    Mathematics 53 (Winter 2009), no. 4, 1109-1126.

    INPUT:

    - ``return_points`` - Boolean (optional) - a value of True returns the points as well as the possible periods.
    
    OUTPUT:
    
    - a list of positive integers, or a list of pairs of projective points and periods if ``flag`` is 1.
    
    Examples::
    
        sage: P.<x,y>=ProjectiveSpace(GF(23),1)
        sage: H=Hom(P,P)
        sage: f=H([x^2-2*y^2,y^2])
        sage: f.possible_periods()
        [1, 5, 11, 22, 110]

    ::

        sage: P.<x,y>=ProjectiveSpace(GF(13),1)
        sage: H=Hom(P,P)
        sage: f=H([x^2-y^2,y^2])
        sage: f.possible_periods(True)
        [[(1 : 0), 1], [(0 : 1), 2], [(3 : 1), 3], [(3 : 1), 36]]

    ::

        sage: PS.<x,y,z>=ProjectiveSpace(2,GF(7))
        sage: H=Hom(PS,PS)
        sage: f=H([-360*x^3 + 760*x*z^2, y^3 - 604*y*z^2 + 240*z^3, 240*z^3])
        sage: f.possible_periods()
        [1, 2, 4, 6, 12, 14, 28, 42, 84]
        
    .. TODO::

        - do not reutrn duplicate points

        - check == False to speed up?

    """
    cdef int i, k
    cdef list pointslist

    if not is_PrimeFiniteField(self.domain().base_ring()):
        raise TypeError("Must be prime field")
    from sage.schemes.projective.projective_space import is_ProjectiveSpace
    if is_ProjectiveSpace(self.domain())==False or self.domain()!=self.codomain():
        raise NotImplementedError("Must be an endomorphism of projective space")

    PS=self.domain()
    p=PS.base_ring().order()
    N=PS.dimension_relative()

    point_table=[[0,0] for i in xrange(p**(N+1))]
    index=1
    periods=set()
    points_periods=[]
    
    for P in _enum_points(p,N):

        hash_p=_hash(P,p)
        if point_table[hash_p][1]==0:
            startindex=index
            while point_table[hash_p][1]==0:
                point_table[hash_p][1]=index
                Q=self._fast_eval(P)
                Q=_normalize_coordinates(Q,p)
                hash_q=_hash(Q,p)
                point_table[hash_p][0]=hash_q
                P=Q
                hash_p=hash_q
                index+=1

            if point_table[hash_p][1]>= startindex:
                P_proj=PS(P)
                period=index-point_table[hash_p][1]
                periods.add(period)
                points_periods.append([P_proj,period])
                l=P_proj.multiplier(self,period,False)
                q=1
                leigen=-1
                while leigen==-1:
                    try:
                        leigen=l.change_ring(GF(p**q,'t')).eigenvalues()
                    except NotImplementedError:
                        q+=5

                lorders=set([])
                for k in xrange(len(leigen)):
                    if leigen[k]!=0:
                        lorders.add(leigen[k].multiplicative_order())

                lorders=list(Set(lorders).subsets())
                rvalues=set()
                for k in xrange(1,len(lorders)):
                    rvalues.add(lcm(lorders[k]))

                rvalues=list(rvalues)
                if N==1:
                    for k in xrange(len(rvalues)):
                        r=rvalues[k]
                        periods.add(period*r)
                        points_periods.append([P_proj,period*r])
                        if p==2 or p==3: #need e=1 for N=1, QQ
                            periods.add(period*r*p)
                            points_periods.append([P_proj,period*r*p])
                else:
                    for k in xrange(len(rvalues)):
                        r=rvalues[k]
                        periods.add(period*r)
                        periods.add(period*r*p)
                        points_periods.append([P_proj,period*r])
                        points_periods.append([P_proj,period*r*p])
                        if p==2:  #need e=3 for N>1, QQ
                            periods.add(period*r*4)
                            points_periods.append([P_proj,period*r*4])
                            periods.add(period*r*8)
                            points_periods.append([P_proj,period*r*8])

    periods=list(periods)
    periods.sort()
    if return_points==False:
        return(periods)
    else:
        return(points_periods)

def _enum_points(int prime,int dimension):
    """
    Enumerate points in projective space with given prime and dimension.

    EXAMPLES::

        sage: from sage.schemes.projective.projective_morphism_helper import _enum_points
        sage: _enum_points(3,2)
        [[1, 0, 0], [0, 1, 0], [1, 1, 0], [2, 1, 0], [0, 0, 1], [1, 0, 1], [2, 0, 1], [0, 1, 1], [1, 1, 1], [2, 1, 1], [0, 2, 1], [1, 2, 1], [2, 2, 1]]

    """
    cdef list ranges=[]
    cdef int curr_prime
    cdef int highest_prime
    
    curr_prime = 1
    highest_prime = prime**dimension
    
    while curr_prime <= highest_prime:
        ranges.append(range(curr_prime,curr_prime*2))
        curr_prime=curr_prime*prime

    cdef list values
    cdef int value
    for values in ranges:
        for value in values:
            yield _get_point_from_hash(value,prime,dimension)

def _hash(list Point,int prime):
    """
    Hash point given as list to unique number.

    EXAMPLES::

        sage: from sage.schemes.projective.projective_morphism_helper import _hash
        sage: _hash([1, 2, 1],3)
        16

    """
    cdef int hash_q
    cdef int coefficient
    
    Point.reverse()
    hash_q=0

    for coefficient in Point:
        hash_q=hash_q*prime+coefficient

    Point.reverse()
    
    return hash_q

def _get_point_from_hash(int value,int prime,int dimension):
    """
    Hash unique number to point as a list.

    EXAMPLES::

        sage: from sage.schemes.projective.projective_morphism_helper import _get_point_from_hash
        sage: _get_point_from_hash(16,3,2)
        [1, 2, 1]

    """
    cdef list P
    cdef int i
    P=[]

    for i in xrange(dimension+1):
        P.append(value%prime)
        value=value/prime

    return P
    
def _mod_inv(int num, int prime):
    """
    Find the mod inverse of the number for the given prime.

    EXAMPLES::

        sage: from sage.schemes.projective.projective_morphism_helper import _mod_inv
        sage: _mod_inv(2,7)
        4

    """
    cdef int a, b, q, t, x, y
    a = prime
    b = num
    x = 1
    y = 0
    while b != 0:
        t = b
        q = a/t
        b = a - q*t
        a = t
        t = x
        x = y - q*t
        y = t

    if y < 0:
        return y + prime
    else:
        return y

def _normalize_coordinates(list point, int prime):
    """
    Normalize the coordinates of the point for the given prime.

    EXAMPLES::

        sage: from sage.schemes.projective.projective_morphism_helper import _normalize_coordinates
        sage: _normalize_coordinates([1,5,1],3)
        [1, 2, 1]

    """
    cdef int last_coefficient, coefficient, mod_inverse
    
    for coefficient in xrange(len(point)):
        point[coefficient] = (point[coefficient]+prime)%prime
        if point[coefficient] != 0:
            last_coefficient = point[coefficient]

    mod_inverse = _mod_inv(last_coefficient,prime)

    for coefficient in xrange(len(point)):
        point[coefficient] = (point[coefficient]*mod_inverse)%prime

    return point