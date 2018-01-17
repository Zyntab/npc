#! /usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from .randweight import randweight
from .classes import *
#import shelve
import random
import app.traits as traits
import app.weights as weightmodule
import app.hedtypes as hedtypes
#import cgi
#import cgitb
#from html_output import *
import app.namn as namn
from app import db, models
import datetime
import ast
from .avrunda import avrunda

#cgitb.enable()


def get_values():
    #formData = cgi.FieldStorage()
    #inputs = {i: formData.getvalue(i) for i in formData}
    #return inputs

    inputs = {'Namn':g.namn,
              'Yrke':'Vanlig',
              'nivå_min':1,
              'nivå_max':3,
              'Ras':'Människa',
              'Kön':'slump',
              'Ålder':'Mogen',
              'Längd':'Medel',
              'Huvudhand':'slump'}
    return inputs

def calc_start_values(inputs, weights):
    output = {}
    #Yrke
    output['Yrke'] = inputs['Yrke']
    #Nivå
    inlvl_min = int(inputs['nivå_min'])
    inlvl_max = int(inputs['nivå_max'])
    if inlvl_min == inlvl_max:
        output['Nivå'] = inlvl_min
    else:
        output['Nivå'] = random.randint(inlvl_min, inlvl_max)
    #Ras
    output['Ras'] = inputs['Ras']
    #Ålder
    if inputs['Ålder'] == 'rng':
        output['Ålder'] = random.randint(int(inputs['ålder_min']), int(inputs['ålder_max']))
    else:
        cats = hedtypes.agetypes[output['Ras']][inputs['Ålder']]
        output['Ålder'] = random.randint(cats[0], cats[1])
    #Ålderskategori
    cats = hedtypes.agecats[output['Ras']]
    if output['Ålder'] <= cats['Ung']:
        output['Ålderskategori'] = 'Ung'
    elif output['Ålder'] <= cats['Mogen']:
        output['Ålderskategori'] = 'Mogen'
    elif output['Ålder'] <= cats['Medel']:
        output['Ålderskategori'] = 'Medel'
    elif output['Ålder'] <= cats['Gammal']:
        output['Ålderskategori'] = 'Gammal'
    else:
        output['Ålderskategori'] = 'Åldring'
    #Kön
    if inputs['Kön'] == 'slump':
        output['Kön'] = random.choice(['Man', 'Kvinna'])
    else:
        output['Kön'] = inputs['Kön']
    #Namn
    if inputs['Namn'] == '*slump*':
        output['Namn'] = random.choice(namn.namn[output['Kön']])
    else:
        output['Namn'] = inputs['Namn']
    #Längd
    if inputs['Längd'] == 'rng':
        output['Längd'] = random.randint(int(inputs['längd_min']), int(inputs['längd_max']))
    else:
        x, y = hedtypes.heights[output['Ras']][output['Kön']][inputs['Längd']]
        output['Längd'] = random.randint(x, y)
    #Huvudhand
    if inputs['Huvudhand'] == 'slump':
        output['Huvudhand'] = randweight(weightmodule.hand)
    else:
        output['Huvudhand'] = inputs['Huvudhand']

    return output

def racemods(char_traits, race):
    traits = char_traits
    for i in hedtypes.race_mods[race]:
        traits[i] += hedtypes.race_mods[race][i]
    return traits

def agemods(char_traits, agetype):
    traits = char_traits
    for i in hedtypes.age_mods[agetype]:
        traits[i] += hedtypes.age_mods[agetype][i]
    return traits

def gendermods(char_traits, race, gender):
    traits = char_traits
    for i in hedtypes.gender_mods[race][gender]:
        traits[i] += hedtypes.gender_mods[race][gender][i]
    return traits

def calc_start_points(level, age):
    start_points = 15
    if level > 1: start_points += 2
    start_points += int(avrunda(None, age/4))
    start_points += (level-1)*4
    return start_points

def create_char(values):
    char_traits = dict(traits.start_traits)
    inputs = values
    weights = dict(weightmodule.weights[inputs['Yrke']])
    start_values = calc_start_values(inputs, weights)
    char_traits = racemods(char_traits, start_values['Ras'])
    char_traits = agemods(char_traits, start_values['Ålderskategori'])
    char_traits = gendermods(char_traits, start_values['Ras'], start_values['Kön'])
    points = calc_start_points(start_values['Nivå'], start_values['Ålder'])
    return Npc(start_values, weights, char_traits, points)

def load_char(charname, user):
    ### ast.literal_eval ###
    c = user.characters.filter_by(name=charname).first()
    lit_eval = ast.literal_eval
    values = {'id':c.id,
              'timestamp':c.timestamp,
              'name':c.name,
              'trace_buys':lit_eval(c.trace_buys),
              'start_values':lit_eval(c.start_values),
              'weights':lit_eval(c.weights),
              'traits':lit_eval(c.traits),
              'points_left':c.points_left,
              'skills':lit_eval(c.skills),
              'hitpoints':lit_eval(c.hitpoints),
              'move_carry':lit_eval(c.move_carry),
              'campaign':c.campaign,
              'notes':c.notes}
    return LoadNpc(values, user)
              

def unique_charname(name, user):
    charnames = []
    for c in user.characters.all():
        charnames.append(ast.literal_eval(c.start_values)['Namn'])
    if name not in charnames:
        return name
    version = 2
    while True:
        new_name = name + str(version)
        if new_name not in charnames:
            break
        version += 1
    return new_name

def save_char(char, user):
    ### Om det är en laddad karaktär som byter namn ska befintlig ändras ###
    ###    i stället för att en ny skapas ###
    character = models.Character(creator=user,
                                 timestamp = datetime.datetime.utcnow(),
                                 name = unique_charname(char['start_values']['Namn'].split()[0], user),
                                 trace_buys = str(char['trace_buys']),
                                 start_values = str(char['start_values']),
                                 weights = str(char['weights']),
                                 traits = str(char['traits']),
                                 points_left = char['points_left'],
                                 skills = str(char['skills']),
                                 hitpoints = str(char['hitpoints']),
                                 move_carry = str(char['move_carry']),
                                 campaign = char['campaign'],
                                 notes = char['notes'])
    db.session.add(character)
    db.session.commit()
    return character
    

if __name__ == '__main__':
    try:
        htmlTop()
        
        char_traits = traits.start_traits
        
        inputs = get_values()           # get values from form

        weights = weightmodule.weights[inputs['Yrke']]

        start_values = calc_start_values(inputs, weights) # calculate start values

        #racemods
        char_traits = racemods(char_traits, start_values['Ras'])

        #agemods
        char_traits = agemods(char_traits, start_values['Ålderskategori'])
        
        #gendermods
        char_traits = gendermods(char_traits, start_values['Ras'], start_values['Kön'])

        #startpoang
        points = calc_start_points(start_values['Nivå'], start_values['Ålder'])
        
        #make class
        char = Npc(start_values, weights, char_traits, points)

        #print results
        printChar(char)
        
        htmlTail()
    except:
        cgi.print_exception()
