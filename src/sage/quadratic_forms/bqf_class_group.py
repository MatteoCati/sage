r"""
Class groups of binary quadratic forms

EXAMPLES:

Constructing the class of a given binary quadratic form is straightforward::

    sage: F1 = BinaryQF([22, 91, 99])
    sage: cl1 = F1.form_class(); cl1
    Class of 5*x^2 - 3*x*y + 22*y^2

Every class is represented by a reduced form in it::

    sage: cl1.form()
    5*x^2 - 3*x*y + 22*y^2
    sage: cl1.form() == F1.reduced_form()
    True

Addition of form classes and derived operations are defined by composition
of binary quadratic forms::

    sage: F2 = BinaryQF([4, 1, 27])
    sage: cl2 = F2.form_class(); cl2
    Class of 4*x^2 + x*y + 27*y^2
    sage: cl1 + cl2
    Class of 9*x^2 + x*y + 12*y^2
    sage: cl1 + cl2 == (F1 * F2).form_class()
    True
    sage: -cl1
    Class of 5*x^2 + 3*x*y + 22*y^2
    sage: cl1 - cl1
    Class of x^2 + x*y + 108*y^2

The form class group can be constructed as an explicit parent object::

    sage: F1.discriminant()
    -431
    sage: Cl = BQFClassGroup(-431); Cl
    Form Class Group of Discriminant -431
    sage: cl1.parent() is Cl
    True
    sage: Cl(F1) == cl1
    True

Structural properties of the form class group, such as the class number,
the group invariants, and element orders, can be computed::

    sage: Cl.order()
    21
    sage: cl1 * Cl.order() == Cl.zero()
    True
    sage: cl2 * Cl.order() == Cl.zero()
    True
    sage: cl2.order()
    7
    sage: cl2 * cl2.order() == Cl.zero()
    True
    sage: Cl.abelian_group()
    Additive abelian group isomorphic to Z/21 embedded in Form Class Group of Discriminant -431
    sage: Cl.gens()  # random
    [Class of 5*x^2 + 3*x*y + 22*y^2]
    sage: Cl.gens()[0].order()
    21

AUTHORS:

- Lorenz Panny (2023)
"""

# ****************************************************************************
#       Copyright (C) 2023 Lorenz Panny
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

from sage.misc.cachefunc import cached_method

from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element import AdditiveGroupElement

from sage.misc.prandom import randrange
from sage.rings.integer_ring import ZZ
from sage.groups.generic import order_from_multiple, multiple
from sage.groups.additive_abelian.additive_abelian_wrapper import AdditiveAbelianGroupWrapper
from sage.quadratic_forms.binary_qf import BinaryQF

from sage.libs.pari import pari


class BQFClassGroup(Parent, UniqueRepresentation):
    r"""
    This type represents the class group for a given discriminant `D`.

    - For `D < 0`, the group is the class group of *positive definite*
      binary quadratic forms. The "full" form class group is the direct
      sum of two isomorphic copies of this group (one for positive
      definite forms and one for negative definite forms).

    - For `D > 0`, this functionality is currently not implemented.

    EXAMPLES::

        sage: BQFClassGroup(-4)
        Form Class Group of Discriminant -4
        sage: BQFClassGroup(-6)
        Traceback (most recent call last):
        ...
        ValueError: not a discriminant

    The discriminant need not be fundamental::

        sage: BQFClassGroup(-22^2)
        Form Class Group of Discriminant -484
    """

    def __init__(self, D, *, check=True):
        r"""
        Construct the class group for a given discriminant `D`.

        TESTS:

        Check that positive discriminants are rejected until code is
        written for them::

            sage: BQFClassGroup(101)
            Traceback (most recent call last):
            ...
            NotImplementedError: positive discriminants are not yet supported
        """
        self._disc = ZZ(D)
        if check:
            if not self._disc or self._disc % 4 not in (0,1):
                raise ValueError('not a discriminant')
            if self._disc > 0:
                raise NotImplementedError('positive discriminants are not yet supported')
        super().__init__()

    def _element_constructor_(self, F, *, check=True):
        r"""
        Construct an element of this form class group as a :class:`BQFClassGroup_element`.

        EXAMPLES::

            sage: Cl = BQFClassGroup(-999)
            sage: Cl(0)                         # indirect doctest
            Class of x^2 + x*y + 250*y^2
            sage: Cl(BinaryQF([16, 5, 16]))     # indirect doctest
            Class of 16*x^2 + 5*x*y + 16*y^2
        """
        if isinstance(F, BQFClassGroup_element):
            if check and F.parent() is not self:  # class group is unique parent
                raise ValueError('quadratic form has incorrect discriminant')
            return F
        if F == 0:
            return self.zero()
        if check and not isinstance(F, BinaryQF):
            raise TypeError('not a binary quadratic form')
        return BQFClassGroup_element(F, parent=self, check=check)

    def zero(self):
        r"""
        Return the neutral element of this group, i.e., the class of the
        principal binary quadratic form of the respective discriminant.

        EXAMPLES::

            sage: Cl = BQFClassGroup(-999)
            sage: cl = Cl.zero(); cl
            Class of x^2 + x*y + 250*y^2
            sage: cl + cl == cl
            True
        """
        return self(BinaryQF.principal(self._disc))

    def random_element(self):
        r"""
        Return a somewhat random element of this form class group.

        ALGORITHM: :meth:`BinaryQF.random`

        .. NOTE::

            No guarantees are being made about the distribution of classes
            sampled by this function. Heuristically, however, it should be
            fairly close to uniform.

        EXAMPLES::

            sage: Cl = BQFClassGroup(-999); Cl
            Form Class Group of Discriminant -999
            sage: cl = Cl.random_element(); cl  # random
            Class of 10*x^2 + x*y + 25*y^2
            sage: cl.form().discriminant()
            -999
        """
        return self(BinaryQF.random(self._disc))

    def __hash__(self):
        r"""
        Return a hash value for this form class group.

        EXAMPLES::

            sage: hash(BQFClassGroup(-999))  # random
            -4246560339810542104
        """
        return hash(('BQFClassGroup', self._disc))

    def _repr_(self):
        r"""
        Return a string describing this form class group.

        EXAMPLES::

            sage: BQFClassGroup(-999)  # indirect doctest
            Form Class Group of Discriminant -999
        """
        return f'Form Class Group of Discriminant {self._disc}'

    def discriminant(self):
        r"""
        Return the discriminant of the forms in this form class group.

        EXAMPLES::

            sage: BQFClassGroup(-999).discriminant()
            -999
        """
        return self._disc

    @cached_method
    def order(self):
        r"""
        Return the order of this form class group (the *class number*).

        ALGORITHM: :pari:`qfbclassno`

        EXAMPLES::

            sage: BQFClassGroup(-4).order()
            1
            sage: BQFClassGroup(-11).order()
            1
            sage: BQFClassGroup(-67).order()
            1
            sage: BQFClassGroup(-163).order()
            1
            sage: BQFClassGroup(-999).order()
            24
            sage: BQFClassGroup(-9999).order()
            88
            sage: BQFClassGroup(-99999).order()
            224
        """
        return ZZ(pari.qfbclassno(self._disc))

    cardinality = order

    @cached_method
    def abelian_group(self):
        r"""
        Return the structure of this form class group as an
        :class:`AdditiveAbelianGroupWrapper` object.

        ALGORITHM: :pari:`quadclassunit`

        EXAMPLES::

            sage: Cl = BQFClassGroup(-4*777)
            sage: Cl.order()
            16
            sage: G = Cl.abelian_group(); G
            Additive abelian group isomorphic to Z/4 + Z/2 + Z/2 embedded in Form Class Group of Discriminant -3108
            sage: G.gens()  # random
            (Class of 11*x^2 + 4*x*y + 71*y^2,
             Class of 6*x^2 + 6*x*y + 131*y^2,
             Class of 2*x^2 + 2*x*y + 389*y^2)
            sage: [g.order() for g in G.gens()]
            [4, 2, 2]
            sage: G.discrete_log(Cl.random_element())  # random
            (3, 0, 1)
        """
        h, ords, gens, reg = pari.quadclassunit(self._disc)
        ords = [ZZ(o) for o in ords]
        gens = [BinaryQF(g) for g in gens]
        return AdditiveAbelianGroupWrapper(self, gens, ords)

    def gens(self):
        r"""
        Return a generating set of this form class group.

        EXAMPLES::

            sage: Cl = BQFClassGroup(-4*419)
            sage: Cl.gens()
            [Class of 3*x^2 + 2*x*y + 140*y^2]

        ::

            sage: Cl = BQFClassGroup(-4*777)
            sage: Cl.gens()  # random
            [Class of 11*x^2 + 4*x*y + 71*y^2,
             Class of 6*x^2 + 6*x*y + 131*y^2,
             Class of 2*x^2 + 2*x*y + 389*y^2]
        """
        return [g.element() for g in self.abelian_group().gens()]


class BQFClassGroup_element(AdditiveGroupElement):
    r"""
    This type represents elements of class groups of binary quadratic forms.

    Users should not need to construct objects of this type directly; it can
    be accessed via either the :class:`BQFClassGroup` parent object or the
    :meth:`~BinaryQF.form_class` method associated to binary quadratic forms.

    Currently only classes of positive definite forms are supported.

    EXAMPLES::

        sage: F = BinaryQF([22, 91, 99])
        sage: F.form_class()  # implicit doctest
        Class of 5*x^2 - 3*x*y + 22*y^2

    ::

        sage: Cl = BQFClassGroup(-4*419)
        sage: Cl.zero()
        Class of x^2 + 419*y^2
        sage: Cl.gens()[0]  # implicit doctest
        Class of 3*x^2 + 2*x*y + 140*y^2
    """

    def __init__(self, F, parent, *, check=True, reduce=True):
        r"""
        Constructor for classes of binary quadratic forms.

        EXAMPLES::

            sage: Cl = BQFClassGroup(-431)
            sage: F = BinaryQF([22, 91, 99])
            sage: from sage.quadratic_forms.bqf_class_group import BQFClassGroup_element
            sage: BQFClassGroup_element(F, parent=Cl)
            Class of 5*x^2 - 3*x*y + 22*y^2
        """
        if check:
            if not isinstance(F, BinaryQF):
                raise TypeError('not a binary quadratic form')
            if F.discriminant() != parent.discriminant():
                raise ValueError('given quadratic form has wrong discriminant')
            if not F.is_primitive():
                raise ValueError('given quadratic form is not primitive')
            if not F.is_positive_definite():
                raise NotImplemented('only positive definite forms are currently supported')
        if reduce:
            F = F.reduced_form()
        self._form = F
        super().__init__(parent=parent)

    def form(self):
        r"""
        Return a reduced quadratic form in this class.

        (For `D < 0`, each class contains a *unique* reduced form.)

        EXAMPLES::

            sage: F = BinaryQF([3221, 2114, 350])
            sage: cl = F.form_class()
            sage: cl.form()
            29*x^2 + 14*x*y + 350*y^2
            sage: cl.form() == F.reduced_form()
            True
        """
        return self._form

    def _neg_(self):
        r"""
        Return the inverse of this form class.

        The inverse class of a form `[a,b,c]` is represented by `[a,-b,c]`.

        EXAMPLES::

            sage: F = BinaryQF([11,21,31])
            sage: cl = F.form_class(); cl
            Class of 11*x^2 - x*y + 21*y^2
            sage: -cl                               # indirect doctest
            Class of 11*x^2 + x*y + 21*y^2
            sage: cl + (-cl) == cl.parent().zero()  # indirect doctest
            True
        """
        a,b,c = self._form
        F = BinaryQF([a,-b,c])
        return BQFClassGroup_element(F, parent=self.parent())

    def _add_(self, other):
        r"""
        Return the composition of two form classes.

        EXAMPLES::

            sage: cl1 = BinaryQF([11,21,31]).form_class(); cl1
            Class of 11*x^2 - x*y + 21*y^2
            sage: cl2 = BinaryQF([7,55,141]).form_class(); cl2
            Class of 7*x^2 - x*y + 33*y^2
            sage: cl1 + cl2                         # indirect doctest
            Class of 3*x^2 + x*y + 77*y^2
        """
        F = self._form * other._form
        return BQFClassGroup_element(F, parent=self.parent())

    def _sub_(self, other):
        r"""
        Return the composition of a form class with the inverse of another.

        EXAMPLES::

            sage: cl1 = BinaryQF([11,21,31]).form_class(); cl1
            Class of 11*x^2 - x*y + 21*y^2
            sage: cl2 = BinaryQF([7,55,141]).form_class(); cl2
            Class of 7*x^2 - x*y + 33*y^2
            sage: cl1 - cl2                         # indirect doctest
            Class of 9*x^2 - 7*x*y + 27*y^2
            sage: cl1 - cl2 == cl1 + (-cl2)         # indirect doctest
            True
        """
        return self + (-other)

    def __mul__(self, other):
        r"""
        Return an integer multiple of this form class with respect to
        repeated composition.

        ALGORITHM: :func:`multiple`

        EXAMPLES::

            sage: F = BinaryQF([11,21,31])
            sage: cl = F.form_class(); cl
            Class of 11*x^2 - x*y + 21*y^2
            sage: cl*0 == cl.parent().zero()        # indirect doctest
            True
            sage: cl*1 == cl                        # indirect doctest
            True
            sage: cl*(-1) == -cl                    # indirect doctest
            True
            sage: cl*2 == cl + cl                   # indirect doctest
            True
            sage: cl*5 == cl + cl + cl + cl + cl    # indirect doctest
            True
            sage: 5*cl == cl*5                      # indirect doctest
            True
            sage: cl*(-5) == -(5*cl)                # indirect doctest
            True
        """
        return multiple(self, other, operation='+')

    __rmul__ = __mul__

    def __eq__(self, other):
        r"""
        Test two form classes for equality.

        EXAMPLES::

            sage: F = BinaryQF([11,21,31])
            sage: cl = F.form_class(); cl
            Class of 11*x^2 - x*y + 21*y^2
            sage: cl == cl      # indirect doctest
            True
            sage: -cl == cl     # indirect doctest
            False
        """
        # When generalizing to positive discriminants in the future, keep
        # in mind that for indefinite forms there can be multiple reduced
        # forms per class. This also affects the other comparison methods
        # as well as hashing.
        return self._form == other._form

    def __ne__(self, other):
        r"""
        Test two form classes for inequality.

        EXAMPLES::

            sage: F = BinaryQF([11,21,31])
            sage: cl = F.form_class(); cl
            Class of 11*x^2 - x*y + 21*y^2
            sage: cl != cl      # indirect doctest
            False
            sage: -cl != cl     # indirect doctest
            True
        """
        return self._form != other._form

    def __lt__(self, other):
        r"""
        Compare two form classes according to the lexicographic ordering
        on their coefficient lists.

        EXAMPLES::

            sage: cl1 = BinaryQF([7,55,141]).form_class(); cl1
            Class of 7*x^2 - x*y + 33*y^2
            sage: cl2 = BinaryQF([11,21,31]).form_class(); cl2
            Class of 11*x^2 - x*y + 21*y^2
            sage: cl1 < cl2     # indirect doctest
            True
            sage: cl1 > cl2     # indirect doctest
            False
        """
        return self._form < other._form

    def __bool__(self):
        r"""
        Return ``True`` if this form class is *not* the principal class
        and ``False`` otherwise.

        EXAMPLES::

            sage: cl = BinaryQF([11,21,31]).form_class()
            sage: bool(cl)
            True
            sage: bool(0*cl)
            False
        """
        return self != self.parent().zero()

    def is_zero(self):
        r"""
        Return ``True`` if this form class is the principal class and
        ``False`` otherwise.

        EXAMPLES::

            sage: cl = BinaryQF([11,21,31]).form_class()
            sage: cl.is_zero()
            False
            sage: (0*cl).is_zero()
            True
        """
        return not self

    def __repr__(self):
        r"""
        Return a string representation of this form class.

        EXAMPLES::

            sage: F = BinaryQF([11,21,31])
            sage: F.form_class()  # indirect doctest
            Class of 11*x^2 - x*y + 21*y^2
        """
        return f'Class of {self._form}'

    def __hash__(self):
        r"""
        Return a hash value for this form class.

        EXAMPLES::

            sage: cl = BinaryQF([11,21,31]).form_class()
            sage: hash(cl)  # random
            -7760578299759721732
        """
        return hash(('BQFClassGroup_element', self._form))

    @cached_method
    def order(self):
        r"""
        Return the order of this form class in its class group.

        ALGORITHM: :meth:`BQFClassGroup.order` and :func:`order_from_multiple`

        EXAMPLES::

            sage: cl = BinaryQF([11,21,31]).form_class()
            sage: cl.order()
            10
            sage: (cl+cl).order()
            5
            sage: (cl+cl+cl).order()
            10
            sage: (5*cl).order()
            2
        """
        return order_from_multiple(self, self.parent().cardinality())
