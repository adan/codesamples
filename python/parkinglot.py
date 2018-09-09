#!/usr/bin/env python
# Copyright (c) 2018 Xiaofan Li
# License: MIT
# @date 2018-09-08

from __future__ import absolute_import, division, print_function, with_statement

from widgets import Enum


# Parking Lot design

class ParkingTimer(object):
    '''ParkingTimer interface.'''
    def getTime(self):
        raise NotImplementedError

class FeeCharger(object):
    '''FeeCharger interface.'''
    def getFee(self, start, end):
        raise NotImplementedError

class ParkingMeter(object):
    '''Parking meter to record start time and end time.'''
    def __init__(self):
        self._startTime = None
        self._endTime = None

    @property
    def startTime(self):
        return self._startTime

    @startTime.setter
    def startTime(self, startTime):
        self._startTime = startTime

    @property
    def endTime(self):
        return self._endTime

    @endTime.setter
    def endTime(self, endTime):
        self._endTime = endTime

ParkingSpaceType = Enum([
    'REGULAR',
    'LARGE',
])

class ParkingSpace(object):
    '''Parking space to store vehicle.'''
    def __init__(self, spaceId, spaceType=ParkingSpaceType.REGULAR, timer=ParkingTimer()):
        self._spaceId = spaceId
        self._spaceType = spaceType
        self.timer = timer
        self.meter = ParkingMeter()

    @property
    def spaceId(self):
        return self._spaceId

    @property
    def spaceType(self):
        return self._spaceType

    def startParking(self):
        self.meter.startTime = self.timer.getTime()

    def endParking(self):
        self.meter.endTime = self.timer.getTime()

    def getFee(self, charger):
        return charger.getFee(self.meter.startTime, self.meter.endTime)

class RegularFeeCharger(FeeCharger):
    '''Parking Lot regular fee charger.'''
    def getFee(self, start, end):
        return (end - start) * 0.1

class LargeFeeCharger(FeeCharger):
    '''Parking Lot large fee charger.'''
    def getFee(self, start, end):
        return (end - start) * 0.5

class ParkingLot(object):
    def __init__(self, spaceCounts, timer, chargers=None):
        nextSpaceId = 1
        self.timer = timer
        if chargers:
            self.chargers = chargers
        else:
            self.chargers = [RegularFeeCharger(), LargeFeeCharger()]
        # Regular spaces
        self.regularSpaces = [ParkingSpace(nextSpaceId+i, timer=self.timer) for i in range(spaceCounts[0])]
        nextSpaceId += spaceCounts[0]
        # Large spaces
        self.largeSpaces = [ParkingSpace(nextSpaceId+i, spaceType=ParkingSpaceType.LARGE, timer=self.timer)
                for i in range(spaceCounts[1])]
        nextSpaceId += spaceCounts[1]

    def getSpaceContainer(self, spaceType):
        if spaceType == ParkingSpaceType.REGULAR:
            return self.regularSpaces
        elif spaceType == ParkingSpaceType.LARGE:
            return self.largeSpaces
        else:
            # Invalid space type.
            return None

    def getFeeCharger(self, spaceType):
        if spaceType == ParkingSpaceType.REGULAR:
            return self.chargers[0]
        elif spaceType == ParkingSpaceType.LARGE:
            return self.chargers[1]
        else:
            # Invalid space type.
            return None

    def allocSpace(self, spaceType):
        spaceContainer = self.getSpaceContainer(spaceType)
        if not spaceContainer:
            return None
        space = spaceContainer.pop(0)
        if not space:
            return None
        space.startParking()
        return space

    def returnSpace(self, space):
        space.endParking()
        fee = space.getFee(self.getFeeCharger(space.spaceType))
        spaceContainer = self.getSpaceContainer(space.spaceType)
        spaceContainer.append(space)
        return fee

class Vehicle(object):
    def park(self, lot):
        raise NotImplementedError

    def unpark(self, lot):
        if self.space:
            fee = lot.returnSpace(self.space)
            self.space = None
            return fee
        return -1

    def getSpaceId(self):
        return self.space.spaceId if self.space else -1

class Car(Vehicle):
    def park(self, lot):
        self.space = lot.allocSpace(ParkingSpaceType.REGULAR)
        return True if self.space else False

class Truck(Vehicle):
    def park(self, lot):
        self.space = lot.allocSpace(ParkingSpaceType.LARGE)
        return True if self.space else False


import unittest


class MockParkingTimer(ParkingTimer):
    def __init__(self, times):
        self.times = times

    def getTime(self):
        return self.times.pop(0)

class ParkingTest(unittest.TestCase):
    def setUp(self):
        self.lot = None

    def tearDown(self):
        del self.lot

    def testParking(self):
        self.lot = ParkingLot([1, 2], timer=MockParkingTimer([1,2,3,4,5,6,7,8]))
        c1, c2, c3 = Car(), Car(), Car()
        self.assertTrue(c1.park(self.lot))
        self.assertFalse(c2.park(self.lot))
        t1, t2, t3 = Truck(), Truck(), Truck()
        self.assertTrue(t1.park(self.lot))
        self.assertTrue(t2.park(self.lot))
        self.assertFalse(t3.park(self.lot))
        self.assertEqual(c1.getSpaceId(), 1)
        self.assertEqual(t1.getSpaceId(), 2)
        self.assertEqual(t2.getSpaceId(), 3)
        self.assertEqual(t2.unpark(self.lot), 0.5) # (4-3) * 0.5
        self.assertEqual(c1.unpark(self.lot), 0.4) # (5-1) * 0.1
        self.assertEqual(t1.unpark(self.lot), 2.0) # (6-2) * 0.5
        self.assertTrue(c3.park(self.lot))
        self.assertEqual(c3.getSpaceId(), 1)
        self.assertEqual(c3.unpark(self.lot), 0.1) # (8-7) * 0.1
        self.assertEqual(c3.getSpaceId(), -1)


if __name__ == '__main__':
    unittest.main()
