r"""
Regular Supercrystals
"""

#*****************************************************************************
#       Copyright (C) 2017 Franco Saliola <saliola@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from __future__ import print_function

from sage.misc.cachefunc import cached_method
from sage.misc.lazy_attribute import lazy_attribute
from sage.categories.category_singleton import Category_singleton
from sage.categories.crystals import Crystals
from sage.categories.tensor import TensorProductsCategory
from sage.combinat.subset import Subsets
from sage.graphs.dot2tex_utils import have_dot2tex

class RegularSuperCrystals(Category_singleton):
    def super_categories(self):
        r"""
        EXAMPLES::

            sage: from sage.categories.regular_supercrystals import RegularSuperCrystalCategory
            sage: RegularSuperCrystalCategory().super_categories()
            [Category of finite crystals]
        """
        return [Crystals().Finite()]

    class ParentMethods:
        @cached_method
        def digraph(self):
            r"""
            EXAMPLES::

                sage: from bkk_crystals import BKKOneBoxCrystal
                sage: c = BKKOneBoxCrystal(2, 3)
                sage: c.digraph()
                Digraph on 5 vertices
            """
            from sage.graphs.digraph import DiGraph
            from sage.misc.latex import LatexExpr
            from sage.combinat.root_system.cartan_type import CartanType

            d = {x: {} for x in self}
            for i in self.index_set():
                for x in d:
                    y = x.f(i)
                    if y is not None:
                        d[x][y] = i
            G = DiGraph(d, format='dict_of_dicts')

            def edge_options((u, v, l)):
                edge_opts = { 'edge_string': '->', 'color': 'black' }
                if l > 0:
                    edge_opts['color'] = CartanType._colors.get(l, 'black')
                    edge_opts['label'] = LatexExpr(str(l))
                elif l < 0:
                    edge_opts['color'] = "dashed," + CartanType._colors.get(-l, 'black')
                    edge_opts['label'] = LatexExpr("\\overline{%s}" % str(-l))
                else:
                    edge_opts['color'] = "dotted," + CartanType._colors.get(l, 'black')
                    edge_opts['label'] = LatexExpr(str(l))
                return edge_opts

            G.set_latex_options(format="dot2tex", edge_labels=True, edge_options=edge_options)

            return G

        def connected_components_generators(self):
            r"""
            EXAMPLES::

                sage: from bkk_crystals import BKKOneBoxCrystal
                sage: c = BKKOneBoxCrystal(2, 3)
                sage: c.connected_components_generators()
                [(-2,)]

                sage: t = c.tensor(c)
                sage: t.connected_components_generators()
                [([-2, -1],), ([-2, -2],)]

                sage: t = c.tensor(c)
                sage: s1, s2 = t.connected_components()
                sage: s = s1 + s2
                sage: s.connected_components_generators()
                [([-2, -1],), ([-2, -2],)]
            """
            # NOTE: we compute the connected components of the digraph,
            # then highest weight elements in each connected components
            X = []
            for connected_component_vertices in self.digraph().connected_components():
                gens = [g for g in connected_component_vertices if g.is_highest_weight()]
                X.append(tuple(gens))
            return X

        def connected_components(self):
            r"""
            EXAMPLES::

                sage: from bkk_crystals import BKKOneBoxCrystal
                sage: c = BKKOneBoxCrystal(2, 3)
                sage: c.connected_components()
                [Subcrystal of BKK crystal on semistandard tableaux of shape [1] with entries in (-2, -1, 1, 2, 3)]
                sage: t = c.tensor(c)
                sage: t.connected_components()
                [Subcrystal of <class 'bkk_crystals.TensorProductOfSuperCrystals_with_category'>,
                 Subcrystal of <class 'bkk_crystals.TensorProductOfSuperCrystals_with_category'>]
            """
            category = RegularSuperCrystals()
            index_set = self.index_set()
            cartan_type = self.cartan_type()
            CCs = []

            for mg in self.connected_components_generators():
                if not isinstance(mg, tuple):
                    mg = (mg,)
                subcrystal = self.subcrystal(generators=mg,
                                             index_set=index_set,
                                             cartan_type=cartan_type,
                                             category=category)
                CCs.append(subcrystal)

            return CCs

        def tensor(self, *crystals, **options):
            """
            Return the tensor product of ``self`` with the crystals ``B``.

            EXAMPLES::
            """
            cartan_type = self.cartan_type()
            from sage.combinat.crystals.tensor_product import FullTensorProductOfSuperCrystals
            if any(c.cartan_type() != cartan_type for c in crystals):
                raise ValueError("all crystals must be of the same Cartan type")
            return FullTensorProductOfSuperCrystals((self,) + tuple(crystals), **options)

        def character(self):
            from sage.rings.all import ZZ
            A = self.weight_lattice_realization().algebra(ZZ)
            return A.sum(A(x.weight()) for x in self)

    class ElementMethods:
        def epsilon(self, i):
            string_length = 0
            x = self
            while True:
                x = x.e(i)
                if x is None:
                    return string_length
                else:
                    string_length += 1

        def phi(self, i):
            string_length = 0
            x = self
            while True:
                x = x.f(i)
                if x is None:
                    return string_length
                else:
                    string_length += 1

    class TensorProducts(TensorProductsCategory):
        """
        The category of regular crystals constructed by tensor
        product of regular crystals.
        """
        @cached_method
        def extra_super_categories(self):
            """
            EXAMPLES::

                sage: RegularCrystals().TensorProducts().extra_super_categories()
                [Category of regular crystals]
            """
            return [self.base_category()]

