#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# This file is part of the SigBit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
#
# common utility functions for SigBit


def ditlen(wpm):
    """returns the lenght of a dit in seconds for a given words-per-minute"""
    #PARIS incl. Abstände == 50 ditlängen -> 1 ditlänge at1wpm = 60s / (50 * wpm)
    return 60 / (50 * wpm)


###morse LUT###
morse = {
	"0" : "-----", "1" : ".----", "2" : "..---", "3" : "...--", "4" : "....-", "5" : ".....",
	"6" : "-....", "7" : "--...", "8" : "---..", "9" : "----.",
	"a" : ".-", "b" : "-...", "c" : "-.-.", "d" : "-..", "e" : ".", "f" : "..-.", "g" : "--.",
	"h" : "....", "i" : "..", "j" : ".---", "k" : "-.-", "l" : ".-..", "m" : "--", "n" : "-.",
	"o" : "---", "p" : ".--.", "q" : "--.-", "r" : ".-.", "s" : "...", "t" : "-", "u" : "..-",
	"v" : "...-", "w" : ".--", "x" : "-..-", "y" : "-.--", "z" : "--..", "=" : "-...-",
	"/" : "-..-.", "+" : ".-.-.", "-" : "-....-", "." : ".-.-.-", "," : "--..--", "?" : "..--..",
	":" : "---...", "!" : "-.-.--", "'" : ".----.", ";" : "-.-.-.", "&" : ".-...", "@" : ".--.-.",
        "ä" : ".-.-", "ö" : "---.", "ü" : "..--", "ch" : "----", '"' : ".-..-.", "(" : "-.--.", ")" : "-.--.-",
        "<sk>" : "...-.-", "<bk>" : "-...-.-"
  }


def encode(text):
    """takes a string of characters and returns a wordbuffer"""
    wordbuffer = []
    for c in text:
        if c == " ":
            wordbuffer.append("11")
        if c in morse:
            for el in morse[c]:
                if el == "-":
                    wordbuffer.append("10")
                if el == ".":
                    wordbuffer.append("01")
            wordbuffer.append("00")
    if len(wordbuffer) > 0:
        wordbuffer.pop()
    wordbuffer.append("11")
    return wordbuffer
                

def decode(buffer):
    """takes a wordbuffer and returns a string of characters"""
    global morse    
    outcode = ""
    outchars = ""
    for el in buffer:
        if el == "01":
            outcode += "."
        elif el == "10":
            outcode += "-"
        elif el == "00":
            
            for letter, code in morse.items():
                if code == outcode:
                    outchars += letter
                    outcode = ""
        elif el =="11":
            for letter, code in morse.items():
                if code == outcode:
                    outchars += letter
                    outcode = ""
                    outchars = outchars + " "
                    return outchars


#make own zfill for uPython
def zfill(str,digits):
    '''we need to implement our own zfill for uPython)'''
    if len(str)>=digits:
        return str
    else:
        return ((digits - len(str)) * '0')+str


#make own ljust for uPython
def ljust(string, width, fillchar=' '):
    '''returns the str left justified, remaining space to the right is filed with fillchar, if str is shorter then width, original string is returned '''
    while len(string) < width:
        string += fillchar
    return string

