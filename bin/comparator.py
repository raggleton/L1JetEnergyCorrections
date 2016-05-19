"""
Classes for use when comparing functions/graphs

Example usage:

>>> A = Contribution("a.root", "li1corr_eta_0_0.348")
>>> B = Contribution("b.root", "li1corr_eta_0_0.348")
>>> p = Plot([A, B], "graphfunction", xlim=[0, 50])
>>> p.plot()
>>> p.save("AB.pdf")

"""


import os
import ROOT
import common_utils as cu
import random


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(55)


class MultiFunc(object):
    """Class to handle multiple TF1s, like a TMultiGraph, because ROOT doesn't.

    NOT SOPHISTICATED, JUST A CONTAINER.
    """
    def __init__(self):
        self.funcs = []

    def Add(self, func):
        self.funcs.append(func)

    def Draw(self, option=""):
        """Draw all the TF1s, adjust the axis sizes properly"""
        # if ROOT.gPad:
        #     if not ROOT.gPad.IsEditable():
        #         ROOT.gROOT.MakeDefCanvas()
        #     if "a" in option.lower():
        #         ROOT.gPad.Clear()

        # Draw, and figure out max/min of axes for some auto-ranging
        x_low, x_high = ROOT.Double(0), ROOT.Double(0)
        x_min, x_max = 999, -999
        y_min, y_max = 999, -999
        for i, f in enumerate(self.funcs):
            if i == 0:
                f.Draw(option)
            else:
                f.Draw(option + "SAME")

            f.GetRange(x_low, x_high)
            x_min = x_low if x_low < x_min else x_min
            x_max = x_high if x_high > x_max else x_max
            y_min = f.GetMinimum(x_low, x_high) if f.GetMinimum(x_low, x_high) < y_min else y_min
            y_max = f.GetMaximum(x_low, x_high) if f.GetMaximum(x_low, x_high) > y_max else y_max
        if x_max < x_min:
            raise Exception("MultiFunc: x_min > x_max")
        if y_max < y_min:
            raise Exception("MultiFunc: y_min > y_max")

        print x_min, x_max
        print y_min, y_max

        self.funcs[0].GetXaxis().SetRangeUser(x_min * 0.95, x_max * 1.05)
        self.funcs[0].GetYaxis().SetRangeUser(y_min * 0.95, y_max * 1.05)

    def Mod(self):
        """If we want to do any sort of styling, need to access the first drawn func"""
        return self.funcs[0]


class Contribution(object):
    """Basic class to handle information about one contribution to a canvas."""

    def __init__(self, file_name, obj_name, label="",
                 line_width=1, line_color=ROOT.kRed, line_style=1,
                 marker_size=1, marker_color=ROOT.kRed, marker_style=1):
        """
        file_name: str
            Name of ROOT file to get object from.
        obj_name: str
            Name of object in ROOT file.
        label: str
            Title of contribution, to be used in legend.
        line_width: int
            Width of line.
        line_color: int or ROOT color
            Color of line.
        line_style: int
            Line style.
        marker_size: int
            Size of marker
        marker_color: int or ROOT color
            Color of markers.
        marker_style: int
            Marker style.
        """
        self.file_name = file_name
        self.obj_name = obj_name
        self.label = label
        self.line_width = line_width
        self.line_color = line_color
        self.line_style = line_style
        self.marker_size = marker_size
        self.marker_color = marker_color
        self.marker_style = marker_style

    def get_obj(self):
        """Get object for this contribution."""
        input_file = cu.open_root_file(self.file_name)
        self.obj = cu.get_from_file(input_file, self.obj_name)
        self.obj.SetLineWidth(self.line_width)
        self.obj.SetLineColor(self.line_color)
        self.obj.SetLineStyle(self.line_style)
        self.obj.SetMarkerSize(self.marker_size)
        self.obj.SetMarkerColor(self.marker_color)
        self.obj.SetMarkerStyle(self.marker_style)
        self.obj.SetDirectory(0)
        input_file.Close()
        return self.obj


class Plot(object):
    """
    Basic class to handle information about one plot,
    which can have several contributions.
    """

    def __init__(self, contributions=None, what="graph",
                 title="", xtitle="", ytitle="", xlim=None, ylim=None,
                 legend=True, extend=False):
        """
        contributions: list
            List of Contribution objects.
        what: str
            Options are "graph", "function", "both".
        title: str
            Title of plot.
        xtitle: str
            X axis title.
        ytitle: str
            Y axis title.
        xlim: list
            Limits of x axis. If None then determines suitable limits.
        ylim: list
            Limits of y axis. If None then determines suitable limits.
        legend: bool
            Include legend on plot.
        extend: bool
            Extend functions to cover the whole x axis range.
        """
        self.contributions = contributions if contributions else []
        if what not in ['graph', 'function', 'both']:
            raise RuntimeError("`what` argument must be one of 'graph' 'function' 'both'")
        self.plot_what = what
        self.title = title
        self.xtitle = xtitle
        self.ytitle = ytitle
        self.xlim = xlim
        self.ylim = ylim
        self.do_legend = legend
        self.legend = ROOT.TLegend(0.65, 0.6, 0.87, 0.87) if legend else None
        self.do_extend = extend
        self.container = None
        self.canvas = None
        # self.canvas = ROOT.TCanvas("canv", "", 800, 600)
        # self.canvas.SetTicks(1, 1)

    def add_contribution(self, *contribution):
        """Add Contribution to Plot. Can be single item or list."""
        self.contributions.extend(*contribution)

    def plot(self, draw_opts=None):
        """Make the plot.

        draw_opts: str
            Same options as you would pass to Draw() in ROOT.
        """

        # First make a container
        if self.plot_what in ["graph", "both"]:
            rand = random.randint(0, 100)  # need a unique name
            self.container = ROOT.TMultiGraph("mg%d" % rand, "")
        else:
            self.container = MultiFunc()

        # Now add all the contributions to the container, styling as we go
        if len(self.contributions) == 0:
            raise UnboundLocalError("contributions list is empty")

        for c in self.contributions:
            try:
                obj = c.get_obj().Clone()
            except IOError:
                print "Couldn't get", c.obj_name
                continue

            if self.plot_what == "graph":
                # if drawing only graph, we need to remove the fit if there is one
                obj.GetListOfFunctions().Remove(obj.GetListOfFunctions().At(0))
            else:
                # if drawing function, extend range as per user's request
                if self.do_extend:
                    if self.plot_what == 'function':
                        obj.SetRange(self.xlim[0], self.xlim[1])
                    elif self.plot_what == "both":
                        obj.GetListOfFunctions().At(0).SetRange(self.xlim[0], self.xlim[1])

            self.container.Add(obj)
            if self.do_legend:
                self.legend.AddEntry(obj, c.label, "LP")

        # Plot the container
        # need different default drawing options for TF1s vs TGraphs
        # (ALP won't actually display axis for TF1)
        if draw_opts is None:
            if self.plot_what in ["graph", 'both']:
                draw_opts = "ALP"
            elif self.plot_what in ['function']:
                draw_opts = ""

        # Need a canvas
        # If we have "SAME" then we want to draw this Plot object
        # on the current canvas
        # Otherwise, we create a new one
        if "SAME" in draw_opts:
            self.canvas = ROOT.gPad
            self.canvas.cd()
            print "Using existing canvas", self.canvas.GetName()
        else:
            rand = random.randint(0, 100)  # need a unique name
            self.canvas = ROOT.TCanvas("canv%s" % rand, "", 800, 600)
            self.canvas.SetTicks(1, 1)

        self.container.Draw(draw_opts)

        # Customise
        if self.plot_what != 'function':
            modifier = self.container
        else:
            modifier = self.container.Mod()

        modifier.SetTitle("%s;%s;%s" % (self.title, self.xtitle, self.ytitle))
        if self.xlim:
            modifier.GetXaxis().SetRangeUser(*self.xlim)
        if self.ylim:
            modifier.GetYaxis().SetRangeUser(*self.ylim)

        # Plot legend
        if self.do_legend:
            self.legend.Draw()

    def save(self, filename):
        """Save the plot to file. Do some check to make sure dir exists."""
        filename = os.path.abspath(filename)
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        self.canvas.SaveAs(filename)
