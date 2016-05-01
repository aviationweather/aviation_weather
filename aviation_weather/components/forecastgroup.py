import re

import aviation_weather
from aviation_weather import exceptions
from aviation_weather.exceptions import FromGroupDecodeError, TemporaryGroupDecodeError, ProbabilityGroupDecodeError, \
    BecomingGroupDecodeError


class _ForecastGroup(object):

    def __init__(self, raw):
        try:
            self.wind = aviation_weather.Wind(raw)
            raw = raw.replace(self.wind.raw, "")
        except exceptions.WindDecodeError:
            self.wind = None

        try:
            self.visibility = aviation_weather.Visibility(raw)
            raw = raw.replace(self.visibility.raw, "")
        except exceptions.VisibilityDecodeError:
            self.visibility = None

        r = raw.split()

        # Weather groups
        t = list()
        i = 0
        try:
            while True:
                t.append(aviation_weather.WeatherGroup(r[i]))
                i += 1
        except (exceptions.WeatherGroupDecodeError, IndexError):
            r = r[i:]
        self.weather_groups = tuple(t)

        # Sky conditions
        t = list()
        i = 0
        try:
            while True:
                t.append(aviation_weather.SkyCondition(r[i]))
                i += 1
        except (exceptions.SkyConditionDecodeError, IndexError):
            r = r[i:]
        self.sky_conditions = tuple(t)

    @property
    def raw(self):
        raw = ""
        if self.wind:
            raw += " %s" % self.wind.raw
        if self.visibility:
            raw += " %s" % self.visibility.raw
        for weather_group in self.weather_groups:
            raw += " %s" % weather_group.raw
        for sky_condition in self.sky_conditions:
            raw += " %s" % sky_condition.raw

        if raw:
            return raw[1:]  # strip leading space
        else:
            return ""


# BECoMinG
class BecomingGroup(_ForecastGroup):

    def __init__(self, raw):
        m = re.search(r"\bBECMG (?P<start_time>\d{4})/(?P<end_time>\d{4})\s(?P<remainder>.+)\b", raw)
        if not m:
            raise BecomingGroupDecodeError("BecomingGroup(%r) could not be parsed" % raw)
        start_time = str(m.group("start_time"))
        end_time = str(m.group("end_time"))
        self.start_time = aviation_weather.Time(start_time + "00Z")
        self.end_time = aviation_weather.Time(end_time + "00Z")
        super().__init__(m.group("remainder"))

    @property
    def raw(self):
        return "BECMG %(start_time)s/%(end_time)s %(super)s" % {
            "start_time": self.start_time.raw[:-3],
            "end_time": self.end_time.raw[:-3],
            "super": super().raw
        }


# FroM
class FromGroup(_ForecastGroup):

    def __init__(self, raw):
        m = re.search(r"\bFM(?P<time>\d{6})\s(?P<remainder>.+)\b", raw)
        if not m:
            raise FromGroupDecodeError("FromGroup(%r) could not be parsed" % raw)
        time = str(m.group("time"))
        self.time = aviation_weather.Time(time + "Z")
        super().__init__(m.group("remainder"))

    @property
    def raw(self):
        return "FM%(time)s %(super)s" % {
            "time": self.time.raw[:-1],  # -1 to remove the "Z"
            "super": super().raw
        }


# PROBability
class ProbabilityGroup(_ForecastGroup):

    def __init__(self, raw):
        m = re.search(
            r"\bPROB(?P<probability>\d{2}) (?P<start_time>\d{4})/(?P<end_time>\d{4})\s(?P<remainder>.+)\b", raw)
        if not m:
            raise ProbabilityGroupDecodeError("ProbabilityGroup(%r) could not be parsed" % raw)
        self.probability = int(m.group("probability"))
        start_time = str(m.group("start_time"))
        end_time = str(m.group("end_time"))
        self.start_time = aviation_weather.Time(start_time + "00Z")
        self.end_time = aviation_weather.Time(end_time + "00Z")
        super().__init__(m.group("remainder"))

    @property
    def raw(self):
        return "PROB%(probability)d %(start_time)s/%(end_time)s %(super)s" % {
            "probability": self.probability,
            "start_time": self.start_time.raw[:-3],
            "end_time": self.end_time.raw[:-3],
            "super": super().raw
        }


# TEMPOrary
class TemporaryGroup(_ForecastGroup):

    def __init__(self, raw):
        m = re.search(r"\bTEMPO (?P<start_time>\d{4})/(?P<end_time>\d{4})\s(?P<remainder>.+)\b", raw)
        if not m:
            raise TemporaryGroupDecodeError("TemporaryGroup(%r) could not be parsed" % raw)
        start_time = str(m.group("start_time"))
        end_time = str(m.group("end_time"))
        self.start_time = aviation_weather.Time(start_time + "00Z")
        self.end_time = aviation_weather.Time(end_time + "00Z")
        super().__init__(m.group("remainder"))

    @property
    def raw(self):
        return "TEMPO %(start_time)s/%(end_time)s %(super)s" % {
            "start_time": self.start_time.raw[:-3],
            "end_time": self.end_time.raw[:-3],
            "super": super().raw
        }
