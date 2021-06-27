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
from .LogMag import LogMagChart


logger = logging.getLogger(__name__)


class MagnitudeZChart(FrequencyChart):
    def __init__(self, name=""):
        super().__init__(name)

        self.minDisplayValue = 0
        self.maxDisplayValue = 100

        self.minValue = 0
        self.maxValue = 1
        self.span = 1

    def drawValues(self, qp: QtGui.QPainter):
        if len(self.data) == 0 and len(self.reference) == 0:
            return

        self._set_start_stop()

        # Draw bands if required
        if self.bands.enabled:
            self.drawBands(qp, self.fstart, self.fstop)

        if self.fixedValues:
            maxValue = self.maxDisplayValue
            minValue = self.minDisplayValue
            self.maxValue = maxValue
            if self.logarithmicY and minValue <= 0:
                self.minValue = 0.01
            else:
                self.minValue = minValue
        else:
            # Find scaling
            minValue = 100
            maxValue = 0
            for d in self.data:
                mag = self.magnitude(d)
                if math.isinf(mag): # Avoid infinite scales
                    continue
                if mag > maxValue:
                    maxValue = mag
                if mag < minValue:
                    minValue = mag
            for d in self.reference:  # Also check min/max for the reference sweep
                if d.freq < self.fstart or d.freq > self.fstop:
                    continue
                mag = self.magnitude(d)
                if math.isinf(mag): # Avoid infinite scales
                    continue
                if mag > maxValue:
                    maxValue = mag
                if mag < minValue:
                    minValue = mag

            minValue = 10*math.floor(minValue/10)
            if self.logarithmicY and minValue <= 0:
                minValue = 0.01
            self.minValue = minValue

            maxValue = 10*math.ceil(maxValue/10)
            self.maxValue = maxValue

        span = maxValue-minValue
        if span == 0:
            span = 0.01
        self.span = span

        # We want one horizontal tick per 50 pixels, at most
        horizontal_ticks = math.floor(self.dim.height/50)
        fmt = Format(max_nr_digits=4)
        for i in range(horizontal_ticks):
            y = self.topMargin + round(i * self.dim.height / horizontal_ticks)
            qp.setPen(QtGui.QPen(self.color.foreground))
            qp.drawLine(self.leftMargin - 5, y,
                        self.leftMargin + self.dim.width + 5, y)
            qp.setPen(QtGui.QPen(self.color.text))
            val = Value(self.valueAtPosition(y)[0], fmt=fmt)
            qp.drawText(3, y + 4, str(val))

        qp.drawText(3,
                    self.dim.height + self.topMargin,
                    str(Value(self.minValue, fmt=fmt)))

        self.drawFrequencyTicks(qp)

        self.drawData(qp, self.data, self.color.sweep)
        self.drawData(qp, self.reference, self.color.reference)
        self.drawMarkers(qp)

    def getYPosition(self, d: Datapoint) -> int:
        mag = self.magnitude(d)
        if self.logarithmicY and mag == 0:
            return self.topMargin - self.dim.height
        if math.isfinite(mag):
            if self.logarithmicY:
                span = math.log(self.maxValue) - math.log(self.minValue)
                return self.topMargin + round(
                    (math.log(self.maxValue) - math.log(mag)) / span * self.dim.height)
            return self.topMargin + round((self.maxValue - mag) / self.span * self.dim.height)
        return self.topMargin

    def valueAtPosition(self, y) -> List[float]:
        absy = y - self.topMargin
        if self.logarithmicY:
            span = math.log(self.maxValue) - math.log(self.minValue)
            val = math.exp(math.log(self.maxValue) - absy * span / self.dim.height)
        else:
            val = self.maxValue - (absy / self.dim.height * self.span)
        return [val]

    @staticmethod
    def magnitude(p: Datapoint) -> float:
        return abs(p.impedance())

    def logarithmicYAllowed(self) -> bool:
        return True

    def copy(self):
        new_chart: LogMagChart = super().copy()
        new_chart.span = self.span
        return new_chart
