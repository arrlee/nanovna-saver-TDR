#  NanoVNASaver
#
#  A python program to view and export Touchstone data from a NanoVNA
#  Copyright (C) 2019, 2020  Rune B. Broberg
#  Copyright (C) 2020 NanoVNA-Saver Authors
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import math
import logging
from typing import List

from PyQt5 import QtWidgets, QtGui

from NanoVNASaver.RFTools import Datapoint
from NanoVNASaver.SITools import Format, Value
from .Frequency import FrequencyChart

logger = logging.getLogger(__name__)


class CapacitanceChart(FrequencyChart):
    def __init__(self, name=""):
        super().__init__(name)

        self.minDisplayValue = 0
        self.maxDisplayValue = 100

        self.minValue = -1
        self.maxValue = 1
        self.span = 1

    def drawChart(self, qp: QtGui.QPainter):
        qp.setPen(QtGui.QPen(self.color.text))
        qp.drawText(3, 15, self.name + " (F)")
        qp.setPen(QtGui.QPen(self.color.foreground))
        qp.drawLine(self.leftMargin, 20, self.leftMargin, self.topMargin+self.dim.height+5)
        qp.drawLine(self.leftMargin-5, self.topMargin+self.dim.height,
                    self.leftMargin+self.dim.width, self.topMargin + self.dim.height)
        self.drawTitle(qp)

    def drawValues(self, qp: QtGui.QPainter):
        if len(self.data) == 0 and len(self.reference) == 0:
            return
        pen = QtGui.QPen(self.color.sweep)
        pen.setWidth(self.dim.point)
        line_pen = QtGui.QPen(self.color.sweep)
        line_pen.setWidth(self.dim.line)
        highlighter = QtGui.QPen(QtGui.QColor(20, 0, 255))
        highlighter.setWidth(1)

        self._set_start_stop()

        # Draw bands if required
        if self.bands.enabled:
            self.drawBands(qp, self.fstart, self.fstop)

        if self.fixedValues:
            maxValue = self.maxDisplayValue / 10e11
            minValue = self.minDisplayValue / 10e11
            self.maxValue = maxValue
            self.minValue = minValue
        else:
            # Find scaling
            minValue = 1
            maxValue = -1
            for d in self.data:
                val = d.capacitiveEquivalent()
                if val > maxValue:
                    maxValue = val
                if val < minValue:
                    minValue = val
            for d in self.reference:  # Also check min/max for the reference sweep
                if d.freq < self.fstart or d.freq > self.fstop:
                    continue
                val = d.capacitiveEquivalent()
                if val > maxValue:
                    maxValue = val
                if val < minValue:
                    minValue = val
            self.maxValue = maxValue
            self.minValue = minValue

        span = maxValue - minValue
        if span == 0:
            logger.info("Span is zero for CapacitanceChart, setting to a small value.")
            span = 1e-15
        self.span = span

        target_ticks = math.floor(self.dim.height / 60)
        fmt = Format(max_nr_digits=1)
        for i in range(target_ticks):
            val = minValue + (i / target_ticks) * span
            y = self.topMargin + round((self.maxValue - val) / self.span * self.dim.height)
            qp.setPen(self.color.text)
            if val != minValue:
                valstr = str(Value(val, fmt=fmt))
                qp.drawText(3, y + 3, valstr)
            qp.setPen(QtGui.QPen(self.color.foreground))
            qp.drawLine(self.leftMargin - 5, y, self.leftMargin + self.dim.width, y)

        qp.setPen(QtGui.QPen(self.color.foreground))
        qp.drawLine(self.leftMargin - 5, self.topMargin,
                    self.leftMargin + self.dim.width, self.topMargin)
        qp.setPen(self.color.text)
        qp.drawText(3, self.topMargin + 4, str(Value(maxValue, fmt=fmt)))
        qp.drawText(3, self.dim.height+self.topMargin, str(Value(minValue, fmt=fmt)))
        self.drawFrequencyTicks(qp)

        self.drawData(qp, self.data, self.color.sweep)
        self.drawData(qp, self.reference, self.color.reference)
        self.drawMarkers(qp)

    def getYPosition(self, d: Datapoint) -> int:
        return (
            self.topMargin +
            round((self.maxValue - d.capacitiveEquivalent()) /
                  self.span * self.dim.height))

    def valueAtPosition(self, y) -> List[float]:
        absy = y - self.topMargin
        val = -1 * ((absy / self.dim.height * self.span) - self.maxValue)
        return [val * 10e11]

    def copy(self):
        new_chart = super().copy()
        new_chart.span = self.span
        return new_chart


class InductanceChart(FrequencyChart):
    def __init__(self, name=""):
        super().__init__(name)

        self.minDisplayValue = 0
        self.maxDisplayValue = 100

        self.minValue = -1
        self.maxValue = 1
        self.span = 1

    def drawChart(self, qp: QtGui.QPainter):
        qp.setPen(QtGui.QPen(self.color.text))
        qp.drawText(3, 15, self.name + " (H)")
        qp.setPen(QtGui.QPen(self.color.foreground))
        qp.drawLine(self.leftMargin, 20, self.leftMargin, self.topMargin+self.dim.height+5)
        qp.drawLine(self.leftMargin-5, self.topMargin+self.dim.height,
                    self.leftMargin+self.dim.width, self.topMargin + self.dim.height)
        self.drawTitle(qp)

    def drawValues(self, qp: QtGui.QPainter):
        if len(self.data) == 0 and len(self.reference) == 0:
            return
        pen = QtGui.QPen(self.color.sweep)
        pen.setWidth(self.dim.point)
        line_pen = QtGui.QPen(self.color.sweep)
        line_pen.setWidth(self.dim.line)
        highlighter = QtGui.QPen(QtGui.QColor(20, 0, 255))
        highlighter.setWidth(1)

        self._set_start_stop()

        # Draw bands if required
        if self.bands.enabled:
            self.drawBands(qp, self.fstart, self.fstop)

        if self.fixedValues:
            maxValue = self.maxDisplayValue / 10e11
            minValue = self.minDisplayValue / 10e11
            self.maxValue = maxValue
            self.minValue = minValue
        else:
            # Find scaling
            minValue = 1
            maxValue = -1
            for d in self.data:
                val = d.inductiveEquivalent()
                if val > maxValue:
                    maxValue = val
                if val < minValue:
                    minValue = val
            for d in self.reference:  # Also check min/max for the reference sweep
                if d.freq < self.fstart or d.freq > self.fstop:
                    continue
                val = d.inductiveEquivalent()
                if val > maxValue:
                    maxValue = val
                if val < minValue:
                    minValue = val
            self.maxValue = maxValue
            self.minValue = minValue

        span = maxValue - minValue
        if span == 0:
            logger.info("Span is zero for CapacitanceChart, setting to a small value.")
            span = 1e-15
        self.span = span

        target_ticks = math.floor(self.dim.height / 60)
        fmt = Format(max_nr_digits=1)
        for i in range(target_ticks):
            val = minValue + (i / target_ticks) * span
            y = self.topMargin + round((self.maxValue - val) / self.span * self.dim.height)
            qp.setPen(self.color.text)
            if val != minValue:
                valstr = str(Value(val, fmt=fmt))
                qp.drawText(3, y + 3, valstr)
            qp.setPen(QtGui.QPen(self.color.foreground))
            qp.drawLine(self.leftMargin - 5, y, self.leftMargin + self.dim.width, y)

        qp.setPen(QtGui.QPen(self.color.foreground))
        qp.drawLine(self.leftMargin - 5, self.topMargin,
                    self.leftMargin + self.dim.width, self.topMargin)
        qp.setPen(self.color.text)
        qp.drawText(3, self.topMargin + 4, str(Value(maxValue, fmt=fmt)))
        qp.drawText(3, self.dim.height+self.topMargin, str(Value(minValue, fmt=fmt)))
        self.drawFrequencyTicks(qp)

        self.drawData(qp, self.data, self.color.sweep)
        self.drawData(qp, self.reference, self.color.reference)
        self.drawMarkers(qp)

    def getYPosition(self, d: Datapoint) -> int:
        return (self.topMargin +
                round((self.maxValue - d.inductiveEquivalent()) /
                      self.span * self.dim.height))

    def valueAtPosition(self, y) -> List[float]:
        absy = y - self.topMargin
        val = -1 * ((absy / self.dim.height * self.span) - self.maxValue)
        return [val * 10e11]

    def copy(self):
        new_chart = super().copy()
        new_chart.span = self.span
        return new_chart
