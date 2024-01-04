#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

class lte:
    def __init__(self, mytext):
        self.t = mytext
    def comuni(self):
        c = self.t[1:-1]
        return c
    def gl(self, estensione):
        m = self.comuni() + '.' + estensione
        return m 
    def al(self, par):
        m = par + self.comuni() + par
        return m 

'''
class GL (Comuni):
    def conestensione(self, estensione):

class AL (Comuni):
    def parentesi(self, par):
    '''

x = lte('caaaaaac')
print('Trasformazioni comuni: %s\nLivello GL: %s\nLivello AL:%s' % (x.comuni(), x.gl('xml'), x.al('=')))
