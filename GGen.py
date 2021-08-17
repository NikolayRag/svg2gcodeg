#!/usr/bin/env python

import sys
from . import shapes



class GGen():
    svg_shapes = ('rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path')


    rootET = None

    scale = 1.
    smoothness = 0.02
    precision = 4

    feedRate = 0
    park = False

    preamble = ''
    shapePre = ''
    shapeIn = ''
    shapeOut = ''
    shapeFinal = ''
    postamble = ''



    def __init__(self, _rootET):
        self.rootET = _rootET



    def set(self,
        scale = None,
        smoothness = None,
        precision = None,

        feedRate = None,
        park = None,

        preamble = None,
        shapePre = None,
        shapeIn = None,
        shapeOut = None,
        shapeFinal = None,
        postamble = None,
    ):
        if scale != None: self.scale = scale
        if smoothness != None: self.smoothness = smoothness
        if precision != None: self.precision = precision

        if feedRate != None: self.feedRate = feedRate
        if park != None: self.park = park

        if preamble != None: self.preamble = preamble
        if shapePre != None: self.shapePre = shapePre
        if shapeIn != None: self.shapeIn = shapeIn
        if shapeOut != None: self.shapeOut = shapeOut
        if shapeFinal != None: self.shapeFinal = shapeFinal
        if postamble != None: self.postamble = postamble


    
    def generate(self,
        join=False,

        scale = None,
        smoothness = None,
        precision = None,
    ):
        self.set(scale=scale, smoothness=smoothness, precision=precision)


        outGCode = self.buildHead()

        for elem in self.rootET.iter():
            try:
                _, tag_suffix = elem.tag.split('}')
            except ValueError:
                print('Skip tag:', elem.tag)
                continue

            if tag_suffix in self.svg_shapes:
                shape_class = getattr(shapes, tag_suffix)
                shapesA = self.shapeGen(shape_class(elem))

                self.shapeDecorate(elem, shapesA, outGCode)


        outGCode += self.buildTail()


        return "\n".join(outGCode) if join else outGCode



    def shapeGen(self, _shape):
        gShapesA = []

        cGShape = []
        p = _shape.point_generator(self.smoothness)
        for x,y,start in p:
            if start:
                cGShape = []
                gShapesA.append(cGShape)

            cGShape.append( (self.scale*x, self.scale*y) )


        return gShapesA



    def shapeDecorate(self, _cEl, _shapes, _outCode=[]):
        injectPre = self.buildInline(self.shapePre, _cEl)
        injectFinal = self.buildInline(self.shapeFinal, _cEl, _shapes)


        for cShape in _shapes:
            if len(cShape):
                injectIn = self.buildInline(self.shapeIn, _cEl, cShape[0])
                injectOut = self.buildInline(self.shapeOut, _cEl, cShape)

                if injectPre: _outCode += [injectPre]
                _outCode += self.buildMove(cShape[0])
                if injectIn: _outCode += [injectIn]
                _outCode += self.buildMove(cShape[1:])
                if injectOut: _outCode += [injectOut]

        if injectFinal: _outCode += [injectFinal]


        return _outCode



    def buildInline(self, _tmpl, _el, _arg=None):
        if callable(_tmpl):
            if _arg:
                _tmpl = _tmpl(_el, _arg)
            else:
                _tmpl = _tmpl(_el)

        if not isinstance(_tmpl, str):
            _tmpl = ''

        return _tmpl



    def buildMove(self, _coords):
        if not isinstance(_coords[0], tuple):
            _coords = (_coords,)

        p = self.precision
        return [f"X{round(_x,p)}Y{round(_y,p)}" for _x,_y in _coords]



    def buildHead(self):
        out = []

        out.append(self.preamble)

        if self.feedRate:
            out.append( f'F{self.feedRate}' )

        return out



    def buildTail(self):
        out = []

        if self.park:
            out.append( self.buildMove((0,0)) )

        out.append(self.postamble)

        return out



