import ROOT
from collections import OrderedDict
import numpy as np


class MultiFunc(object):
    """Class to handle using different TF1s over different ranges.

    E.g. y = x for x = [0,1], then y = x^2 for [1, Inf]
    This was created since it is so hard (impossible?) to do in ROOT.

    It is supposed to ducktype TF1, although so far only bare basics implemented.
    """

    def __init__(self, functions_dict):
        """Constructor takes as argument a dictionary, where each key is a tuple,
        and each value is a TF1 object.

        The tuple must have 2 elements: lower and upper bounds, which define the
        valid function range.

        e.g.
        lin = ROOT.TF1("lin", "x")
        quad = ROOT.TF1("quad", "x*x")

        functions_dict = {
            (-np.inf, 1): lin,
            (1, np.inf): quad
        }
        f = c.MultiFunc(functions_dict)
        f.Eval(0.5) # 0.5
        f.Eval(3) # 9
        """
        # Need a OrderedDict to keep ordered by application range
        self.functions_dict = OrderedDict(sorted(functions_dict.items(), key=lambda x: x[0][0]))

    def Eval(self, x):
        """Emulate TF1.Eval() but will call the correct function,
        depending on which function is applicable for the value of x."""
        if x >= self.functions_dict.keys()[-1][1] or x < self.functions_dict.keys()[0][0]:
            raise RuntimeError('x is beyond the limit of your MultiFunc range')
        return [func for lim, func in self.functions_dict.iteritems() if lim[0] <= x < lim[1]][0].Eval(x)

    def Draw(self, draw_args=None, draw_range=None):
        """Draw the complete function.

        draw_args : str
            args to be passed of TF1.Draw()
        draw_range : list[float, float]
            x range to draw function over. if None, will draw over
            whole range of functions specified.
        """
        if not draw_range:
            draw_range = [-np.inf, np.inf]
        if not draw_args or "SAME" not in draw_args:
            # make a 'blank' function to occupy the complete range of x values:
            lower_lim = min([lim[0] for lim in self.functions_dict.keys()])
            if np.isneginf(lower_lim):
                lower_lim = -999
            upper_lim = max([lim[1] for lim in self.functions_dict.keys()])
            if np.isposinf(upper_lim):
                upper_lim = 1024
            if draw_range[0] > lower_lim:
                lower_lim = draw_range[0]
            if draw_range[1] < upper_lim:
                upper_lim = draw_range[1]

            title = self.functions_dict.values()[0].GetTitle()
            if title is None:
                title = ""
            blank = ROOT.TF1("blank" + str(np.random.randint(0, 10000)), title, lower_lim, upper_lim)
            blank.Draw()
            max_value = max([func.GetMaximum(lim[0], lim[1])
                             for lim, func in self.functions_dict.iteritems()]) * 1.1
            blank.SetMaximum(max_value)
            min_value = min([func.GetMinimum(lim[0], lim[1])
                             for lim, func in self.functions_dict.iteritems()]) * 0.9
            blank.SetMinimum(min_value)
            ROOT.SetOwnership(blank, False)  # NEED THIS SO IT ACTUALLY GETS DRAWN. SERIOUSLY, WTF?!
            blank.SetLineColor(ROOT.kWhite)

        # now draw the rest of the functions
        draw_args = "" if not draw_args else draw_args
        for func in self.functions_dict.values():
            func.SetNpx(1000)
            func.Draw("SAME" + draw_args)

    def SetLineColor(self, color):
        for func in self.functions_dict.values():
            func.SetLineColor(color)

    def SetLineWidth(self, width):
        for func in self.functions_dict.values():
            func.SetLineWidth(width)

    def SetTitle(self, title):
        for func in self.functions_dict.values():
            func.SetTitle(title)

    def __repr__(self):
        """str representation. Prints each fns name and range of validity,
        ordered by ascending range
        """
        parts = ["%s: %.2f - %.2f\n%s" % (f.GetName(), r[0], r[1], f.GetExpFormula("P"))
                 for r, f in self.functions_dict.iteritems()]
        return "\n".join(sorted(parts))

    def __str__(self):
        """str representation. Prints each fns name and range of validity,
        ordered by ascending range
        """
        parts = ["%s: %.2f - %.2f\n%s" % (f.GetName(), r[0], r[1], f.GetExpFormula("P"))
                 for r, f in self.functions_dict.iteritems()]
        return "\n".join(sorted(parts))
