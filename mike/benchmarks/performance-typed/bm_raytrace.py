# This file contains definitions for a simple raytracer.
# Copyright Callum and Tony Garnock-Jones, 2008.
# This file may be freely redistributed under the MIT license,
# http://www.opensource.org/licenses/mit-license.php

# from http://www.lshift.net/blog/2008/10/29/toy-raytracer-in-python
from __future__ import with_statement

import math

EPSILON = 0.00001

@fields({'x':float, 'y':float, 'z':float}) 
class Vector(object):
    def __init__(self, initx:float, inity:float, initz:float):
        self.x = initx
        self.y = inity
        self.z = initz

    def __str__(self)->str:
        return '(%s,%s,%s)' % (self.x, self.y, self.z)

    def __repr__(self)->str:
        return 'Vector(%s,%s,%s)' % (self.x, self.y, self.z)

    def magnitude(self)->float:
        return math.sqrt(self.dot(self))

    def __add__(self, other:{'x':float, 'y':float, 'z':float})->{'x':float, 'y':float, 'z':float}:
        if other.isPoint():
            return Point(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other:Vector)->Vector:
        other.mustBeVector()
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def scale(self, factor:float)->Vector:
        return Vector(factor * self.x, factor * self.y, factor * self.z)

    def dot(self, other:Vector)->float:
        other.mustBeVector()
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def cross(self, other:Vector)->float:
        other.mustBeVector()
        return Vector(self.y * other.z - self.z * other.y,
                      self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x)

    def normalized(self)->Vector:
        return self.scale(1.0 / self.magnitude())

    def negated(self)->Vector:
        return self.scale(-1)

    def __eq__(self, other:Vector)->bool:
        return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)

    def isVector(self)->bool:
        return True

    def isPoint(self)->bool:
        return False

    def mustBeVector(self)->Vector:
        return self

    def mustBePoint(self)->Vector:
        raise 'Vectors are not points!'

    def reflectThrough(self, normal:Vector)->Vector:
        d = normal.scale(self.dot(normal))
        return self - d.scale(2)

Vector.ZERO = Vector(0,0,0)
Vector.RIGHT = Vector(1,0,0)
Vector.UP = Vector(0,1,0)
Vector.OUT = Vector(0,0,1)

assert Vector.RIGHT.reflectThrough(Vector.UP) == Vector.RIGHT
assert Vector(-1,-1,0).reflectThrough(Vector.UP) == Vector(-1,1,0)

@fields({'x':float, 'y':float, 'z':float}) 
class Point(object):
    def __init__(self, initx:float, inity:float, initz:float):
        self.x = initx
        self.y = inity
        self.z = initz

    def __str__(self)->str:
        return '(%s,%s,%s)' % (self.x, self.y, self.z)

    def __repr__(self)->str:
        return 'Point(%s,%s,%s)' % (self.x, self.y, self.z)

    def __add__(self, other:Vector)->Point:
        other.mustBeVector()
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other:{'x':float, 'y':float, 'z':float})->{'x':float, 'y':float, 'z':float}:
        if other.isPoint():
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def isVector(self)->bool:
        return False

    def isPoint(self)->bool:
        return True

    def mustBeVector(self)->Vector:
        raise 'Points are not vectors!'

    def mustBePoint(self)->Point:
        return self

@fields({'centre': Point, 'radius':float})
class Sphere(object):
    def __init__(self, centre:Point, radius:float):
        centre.mustBePoint()
        self.centre = centre
        self.radius = radius

    def __repr__(self)->str:
        return 'Sphere(%s,%s)' % (repr(self.centre), self.radius)

    def intersectionTime(self, ray:Ray):
        cp = self.centre - ray.point
        v = cp.dot(ray.vector)
        discriminant = (self.radius * self.radius) - (cp.dot(cp) - v*v)
        if discriminant < 0:
            return None
        else:
            return v - math.sqrt(discriminant)

    def normalAt(self, p:Vector)->Vector:
        return (p - self.centre).normalized()

@fields({'point':Point, 'normal':Vector})
class Halfspace(object):
    def __init__(self, point:Point, normal:Vector):
        self.point = point
        self.normal = normal.normalized()

    def __repr__(self)->str:
        return 'Halfspace(%s,%s)' % (repr(self.point), repr(self.normal))

    def intersectionTime(self, ray:Ray):
        v = ray.vector.dot(self.normal)
        if v:
            return 1 / -v
        else:
            return None

    def normalAt(self, p:Vector)->Vector:
        return self.normal

@fields({'point':Point, 'vector':Vector})
class Ray(object):
    def __init__(self, point:Point, vector:Vector):
        self.point = point
        self.vector = vector.normalized()

    def __repr__(self)->str:
        return 'Ray(%s,%s)' % (repr(self.point), repr(self.vector))

    def pointAtTime(self, t:float)->Point:
        return self.point + self.vector.scale(t)

Point.ZERO = Point(0,0,0)

a = Vector(3,4,12)
b = Vector(1,1,1)

@fields({'width':int, 'height':int, 'filenameBase':str, 'bytes':List(int)})
class PpmCanvas(object):
    def __init__(self, width:int, height:int, filenameBase:str):
        import array
        self.bytes = array.array('B', [0] * (width * height * 3))
        for i in range(width * height):
            self.bytes[i * 3 + 2] = 255
        self.width = width
        self.height = height
        self.filenameBase = filenameBase

    def plot(self, x:int, y:int, r:float, g:float, b:float):
        i = ((self.height - y - 1) * self.width + x) * 3
        self.bytes[i  ] = max(0, min(255, int(r * 255)))
        self.bytes[i+1] = max(0, min(255, int(g * 255)))
        self.bytes[i+2] = max(0, min(255, int(b * 255)))

    def save(self):
        pass
        #with open(self.filenameBase + '.ppm', 'wb') as f:
        #    f.write('P6 %d %d 255\n' % (self.width, self.height))
        #    f.write(self.bytes.tostring())

def firstIntersection(intersections:int): #<- temp
    result = None
    for i in intersections:
        candidateT = i[1]
        if candidateT is not None and candidateT > -EPSILON:
            if result is None or candidateT < result[1]:
                result = i
    return result

@fields({'objects':List(({'intersectionTime':Function([Ray], Dyn)}, SimpleSurface)),
         'lightPoints':List(Point),
         'position':Point,
         'lookingAt': Point,
         'fieldOfView':int,
         'recursionDepth':int})
class Scene(object):
    def __init__(self):
        self.objects = []
        self.lightPoints = []
        self.position = Point(0, 1.8, 10)
        self.lookingAt = Point.ZERO
        self.fieldOfView = 45
        self.recursionDepth = 0

    def moveTo(self, p:Point):
        self.position = p

    def lookAt(self, p:Point):
        self.lookingAt = p

    def addObject(self, object:{'intersectionTime':Function([Ray], Dyn)}, surface:SimpleSurface):
        self.objects.append((object, surface))

    def addLight(self, p:Point):
        self.lightPoints.append(p)

    def render(self, canvas:PpmCanvas):
        #print 'Computing field of view'
        fovRadians = math.pi * (self.fieldOfView / 2.0) / 180.0
        halfWidth = math.tan(fovRadians)
        halfHeight = 0.75 * halfWidth
        width = halfWidth * 2
        height = halfHeight * 2
        pixelWidth = width / (canvas.width - 1)
        pixelHeight = height / (canvas.height - 1)

        eye = Ray(self.position, self.lookingAt - self.position)
        vpRight = eye.vector.cross(Vector.UP).normalized()
        vpUp = vpRight.cross(eye.vector).normalized()

        #print 'Looping over pixels'
        previousfraction = 0
        for y in range(canvas.height):
            currentfraction = float(y) / canvas.height
            if currentfraction - previousfraction > 0.05:
                canvas.save()
                #print '%d%% complete' % (currentfraction * 100)
                previousfraction = currentfraction
            for x in range(canvas.width):
                xcomp = vpRight.scale(x * pixelWidth - halfWidth)
                ycomp = vpUp.scale(y * pixelHeight - halfHeight)
                ray = Ray(eye.point, eye.vector + xcomp + ycomp)
                colour = self.rayColour(ray)
                canvas.plot(x,y,*colour)

        #print 'Complete.'

    def rayColour(self, ray:Ray):
        if self.recursionDepth > 3:
            return (0,0,0)
        try:
            self.recursionDepth = self.recursionDepth + 1
            intersections = [(o, o.intersectionTime(ray), s) for (o, s) in self.objects]
            i = firstIntersection(intersections)
            if i is None:
                return (0,0,0) ## the background colour
            else:
                (o, t, s) = i
                p = ray.pointAtTime(t)
                return s.colourAt(self, ray, p, o.normalAt(p))
        finally:
            self.recursionDepth = self.recursionDepth - 1

    def _lightIsVisible(self, l:Point, p:Vector)->bool:
        for (o, s) in self.objects:
            t = o.intersectionTime(Ray(p,l - p))
            if t is not None and t > EPSILON:
                return False
        return True

    def visibleLights(self, p:Point)->List(Point):
        result = []
        for l in self.lightPoints:
            if self._lightIsVisible(l, p):
                result.append(l)
        return result

def addColours(a:(float,float,float), scale:float, b:(float,float,float))->(float,float,float):
    return (a[0] + scale * b[0],
            a[1] + scale * b[1],
            a[2] + scale * b[2])

@fields({'baseColour':(float,float,float), 'specularCoefficient': float,
         'lambertCoefficient':float, 'ambientCoefficient':float})
class SimpleSurface(object):
    def __init__(self, **kwargs):
        self.baseColour = kwargs.get('baseColour', (1,1,1))
        self.specularCoefficient = kwargs.get('specularCoefficient', 0.2)
        self.lambertCoefficient = kwargs.get('lambertCoefficient', 0.6)
        self.ambientCoefficient = 1.0 - self.specularCoefficient - self.lambertCoefficient

    def baseColourAt(self, p:Point)->(float,float,float):
        return self.baseColour

    def colourAt(self, scene:Scene, ray:Ray, p:Point, normal:Vector)->(float,float,float):
        b = self.baseColourAt(p)

        c = (0,0,0)
        if self.specularCoefficient > 0:
            reflectedRay = Ray(p, ray.vector.reflectThrough(normal))
            #print p, normal, ray.vector, reflectedRay.vector
            reflectedColour = scene.rayColour(reflectedRay)
            c = addColours(c, self.specularCoefficient, reflectedColour)

        if self.lambertCoefficient > 0:
            lambertAmount = 0
            for lightPoint in scene.visibleLights(p):
                contribution = (lightPoint - p).normalized().dot(normal)
                if contribution > 0:
                    lambertAmount = lambertAmount + contribution
            lambertAmount = min(1,lambertAmount)
            c = addColours(c, self.lambertCoefficient * lambertAmount, b)

        if self.ambientCoefficient > 0:
            c = addColours(c, self.ambientCoefficient, b)

        return c

@fields({'otherColour': (float,float,float), 'checkSize': float}) 
class CheckerboardSurface(SimpleSurface):
    def __init__(self, **kwargs):
        SimpleSurface.__init__(self, **kwargs)
        self.otherColour = kwargs.get('otherColour', (0,0,0))
        self.checkSize = kwargs.get('checkSize', 1)

    def baseColourAt(self, p:Point)->(float,float,float):
        v = p - Point.ZERO
        v.scale(1.0 / self.checkSize)
        if (int(abs(v.x) + 0.5) + \
            int(abs(v.y) + 0.5) + \
            int(abs(v.z) + 0.5)) \
           % 2:
            return self.otherColour
        else:
            return self.baseColour

def _main():
    Canvas = PpmCanvas
    c = Canvas(100,100,'test_raytrace')
    #c = Canvas(640,480,'test_raytrace_big')
    s = Scene()
    s.addLight(Point(30, 30, 10))
    s.addLight(Point(-10, 100, 30))
    s.lookAt(Point(0, 3, 0))
    s.addObject(Sphere(Point(1,3,-10), 2), SimpleSurface(baseColour = (1,1,0)))
    for y in range(6):
        s.addObject(Sphere(Point(-3 - y * 0.4, 2.3, -5), 0.4),
                    SimpleSurface(baseColour = (y / 6.0, 1 - y / 6.0, 0.5)))
    s.addObject(Halfspace(Point(0,0,0), Vector.UP), CheckerboardSurface())
    s.render(c)

def main(n:int, timer):
    times = []
    for i in range(5):
        _main() # warmup
    for i in range(n):
        t1 = timer()
        _main()
        t2 = timer()
        times.append(t2 - t1)
    return times

if __name__ == "__main__":
    import util, optparse
    parser = optparse.OptionParser(
        usage="%prog [options]",
        description="Test the performance of the raytrace benchmark")
    util.add_standard_options_to(parser)
    options, args = parser.parse_args()

    util.run_benchmark(options, options.num_runs, main)
