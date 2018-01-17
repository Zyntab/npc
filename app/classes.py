# -*- coding: utf-8 -*-

"""
stores classes with logic for display of traits and using points
"""

import random
from .randweight import randweight
import app.traits as traits
import app.weights as weightsmodule
from .avrunda import avrunda
import importlib
from app import db, models
from .hedtypes import agecats, age_mods

class Npc:
    def trace(self, trait, change):
        if trait in self.trace_buys.keys():
            self.trace_buys[trait] += change
        else:
            self.trace_buys[trait] = change

    def use_points(self, trait):
        if self.points_left >= traits.costs[trait]:
            if trait in traits.doubles:
                for i in traits.doubles[trait]:
                    self.traits[i] += 1
                self.points_left -= traits.costs[trait]
                self.trace_buys.append({'trait':trait,
                                        'cost':traits.costs[trait],
                                        'points left':self.points_left})
                #self.trace(trait, 1)            # trace buys
            elif trait in ['Bas', 'Skol', 'Yrke']:
                self.traits[trait] += 1
                self.points_left -= traits.costs[trait]
                self.trace_buys.append({'trait':trait,
                                        'cost':traits.costs[trait],
                                        'points left':self.points_left})
                #self.trace(trait, 1)
                if trait == 'Skol':
                    if self.traits[trait] % 3 == 0:
                        if self.points_left >= traits.costs['Special_skol']:
                            self.traits['Special_skol'] += 1
                            self.points_left -= traits.costs['Special_skol']
                            self.trace_buys.append({'trait':'Special_skol',
                                                    'cost':traits.costs['Special_skol'],
                                                    'points left':self.points_left})
                            #self.trace('Special_skol', 1)
                        else: pass
                    else: pass
                elif trait == 'Yrke':
                    if self.traits[trait] % 3 == 0:
                        if self.points_left >= traits.costs['Special_yrke']:
                            self.traits['Special_yrke'] += 1
                            self.points_left -= traits.costs['Special_yrke']
                            self.trace_buys.append({'trait':'Special_yrke',
                                                    'cost':traits.costs['Special_yrke'],
                                                    'points left':self.points_left})
                            #self.trace('Special_yrke', 1)
                        else: pass
                    else: pass
            elif trait == 'Special_hobb':
                self.traits[trait] += 1
                self.points_left -= traits.costs[trait]
                self.trace_buys.append({'trait':'Special_hobb',
                                        'cost':traits.costs['Special_hobb'],
                                        'points left':self.points_left})
                #self.trace(trait, 1)
            else: pass
        else: pass

            
                
    def dist_points(self):
        path = self.weights
        while self.points_left > 1:
            mainweights = {key:path[key]['main'] for key in path.keys()}
            main = randweight(mainweights)
            if sum(path[main]['sub'].values()) != 0:
                subweights = path[main]['sub']
                sub = randweight(subweights)
                self.use_points(sub)
        if self.points_left == 1 and self.weights['Färdigheter']['sub']['Special_hobb'] != 0:
            self.use_points('Special_hobb')

    def move_sliders(self):
        for i in ['fys_ment','konst_rörl','snabb_uth','finm_grovm','perc_konc',
                  'prak_teor','log_emo']:
            n = randweight({0:25, 1:20, 2:5, 3:1})
            for t in traits.sliders[i]:
                if n >= self.traits[t]:
                    n = self.traits[t] - 1
            if n != 0:
                if i == 'fys_ment':
                    plus = randweight(weightsmodule.fys_ment[self.start_values['Yrke']])
                    fys_mod = 1 if plus == 'Fysisk' else -1
                    ment_mod = fys_mod * -1
                    while n > 0:
                        change_fys = random.choice(['konst_rörl','snabb_uth','finm_grovm'])
                        for i in traits.doubles[change_fys]:
                            self.traits[i] += (1 * fys_mod)
                        change_ment = random.choice(['perc_konc','prak_teor','log_emo'])
                        for i in traits.doubles[change_ment]:
                            self.traits[i] += (1 * ment_mod)
                        self.trace_buys.append({'fys_ment':{change_fys:(fys_mod),
                                                            change_ment:(ment_mod)}})
                        n -= 1
                else:
                    direction = random.choice(['höger', 'vänster'])
                    if direction == 'höger':
                        self.traits[traits.doubles[i][0]] += n 
                        self.traits[traits.doubles[i][1]] -= n
                    else:
                        self.traits[traits.doubles[i][0]] -= n
                        self.traits[traits.doubles[i][1]] += n
                    self.trace_buys.append({'slider':i,
                                            'direction':direction,
                                            'n':n})
            else: pass

        for i in traits.senses:
            n = randweight({0:240, 1:20, 2:5, 3:1})
            sign = random.choice([1, -1])
            self.traits[i] += (n * sign)
            self.points_left += (n * sign * -1 * traits.costs[i])
            if n != 0:
                self.trace_buys.append({'slider':i,
                                        'n':(n*sign),
                                        'points_left':self.points_left})
                    
                    

    def level_specials(self, n):
        specs = ['Special_skol', 'Special_yrke']
        if self.weights['Färdigheter']['sub']['Special_hobb'] != 0:
            specs.append['Special_hobb']
        for i in range(n):
            trait = random.choice(specs)
            self.traits[trait] += 1
            self.trace_buys.append('level special: %s' % trait)
        

    def calc_skills(self):
        skills = {}
        for i in traits.skills_bases.keys():
            x = traits.skills_bases[i][0]
            y = traits.skills_bases[i][1]
            skills[i] = self.traits[x] + self.traits[y]
        return skills

    def calc_hitpoints(self):
        hp = {}
        k = self.traits['Konstitution'] - 1
        hp['Huvud'] = int(2 + k/2)
        for i in ['Hals', 'Vänster fot', 'Höger fot']:
            hp[i] = int(1 + k/3)
        for i in ['Vänster axel', 'Höger axel']:
            hp[i] = int(4 + k/2)
        hp['Bröstkorg'] = int(4.5 + k/2)
        for i in ['Vänster överarm', 'Höger överarm']:
            hp[i] = int(2.5 + k/2)
        for i in ['Mage', 'Vänster lår', 'Höger lår']:
            hp[i] = int(3 + k/3)
        for i in ['Vänster underarm', 'Höger underarm']:
            hp[i] = int(1.5 + k/2)
        for i in ['Vänster hand', 'Höger hand']:
            hp[i] = int(1 + k/5)
        hp['Höft'] = int(4 + k/3)
        for i in ['Vänster smalben', 'Höger smalben']:
            hp[i] = int(2 + k/3)
        return hp

    def calc_iv(self):
        base = self.traits['Snabbhet']
        if base == 1:
            iv = 24
        elif base == 2:
            iv = 27
        elif base > 5:
            iv = 30 + (base - 5) * 3
        else:
            iv = 30
        for i in ['Perception', 'Koncentration', 'Praktisk', 'Emotionell']:
            iv += self.traits[i]
        return iv

    def calc_move_carry(self):
        res = {}
        res['Normal förflyttning'] = self.start_values['Längd'] * 0.65 / 100
        s, u = self.traits['Snabbhet'], self.traits['Rörlighet']
        res['Sprint'] = (s + u) / 2 * res['Normal förflyttning']
        res['Jogg'] = res['Sprint'] / 2
        res['Normal / 8 h'] = res['Normal förflyttning'] * 3600 * 8 / 1000
        res['Maximal förflyttning'] = self.traits['Uthållighet'] * 5 / 2 * 10
        res['Normal bärförmåga'] = self.traits['Konstitution'] + self.traits['Uthållighet']
        res['Maximal bärförmåga'] = res['Normal bärförmåga'] * 15
        return res
        ##### Must use string formatting to display correct decimals #####

    def round_move_carry(self):
        res = {}
        for i in self.move_carry['exakt']:
            res[i] = avrunda(i, self.move_carry['exakt'][i])
        return res
            

    def __init__(self, start_values, weights, char_traits, points):
        self.trace_buys = [('create char',points)]               # to trace what's been bought
        self.start_values = start_values
        self.weights = weights
        self.traits = char_traits
        self.points_left = points
        self.move_sliders()
        self.dist_points()
        self.level_specials(self.start_values['Nivå'] - 1)
        self.skills = self.calc_skills()
        self.hitpoints = self.calc_hitpoints()
        self.traits['Total IV'] = self.calc_iv()
        self.move_carry = {'exakt': {}, 'avrundat': {}}
        self.move_carry['exakt'] = self.calc_move_carry()
        self.move_carry['avrundat'] = self.round_move_carry()

    def toDict(self):
        return {'trace_buys':str(self.trace_buys),
                'start_values':self.start_values,
                'weights':self.weights,
                'traits':self.traits,
                'points_left':self.points_left,
                'skills':self.skills,
                'hitpoints':self.hitpoints,
                'move_carry':self.move_carry,
                'name':'',
                'campaign':'',
                'notes':''}
                

    def ding(self, lvls, years):
        self.trace_buys.append('DING: %s levels, %s years' % (lvls, years))
        oldlvl = self.start_values['Nivå']
        newlvl = oldlvl + int(lvls)
        oldage = self.start_values['Ålder']
        newage = oldage + int(years)
        points = 0
        if newage != oldage:
            old_age_points = int(avrunda(None, oldage/4))
            new_age_points = int(avrunda(None, newage/4))
            points += (new_age_points - old_age_points)
            self.start_values['Ålder'] = newage
            oldagecat = self.start_values['Ålderskategori']
            cats = dict(agecats[self.start_values['Ras']])
            if newage <= cats['Ung']:
                newagecat = 'Ung'
            elif newage <= cats['Mogen']:
                newagecat = 'Mogen'
            elif newage <= cats['Medel']:
                newagecat = 'Medel'
            elif newage <= cats['Gammal']:
                newagecat = 'Gammal'
            else:
                newagecat = 'Åldring'
            if newagecat != oldagecat:
                self.trace_buys.append('Ändra ålderskategori: %s => %s' % (oldagecat, newagecat))
                self.change_agecat(oldagecat, newagecat)
                self.start_values['Ålderskategori'] = newagecat
        if newlvl != oldlvl:
            points += int(lvls) * 4
            if oldlvl == 1:
                points += 2
            self.start_values['Nivå'] = newlvl
        self.points_left += points
        self.trace_buys.append('Sparade poäng: +%s' % points)
        self.dist_points()
        self.level_specials(int(lvls))
        self.skills = self.calc_skills()
        self.hitpoints = self.calc_hitpoints()
        self.traits['Total IV'] = self.calc_iv()
        self.move_carry['exakt'] = self.calc_move_carry()
        self.move_carry['avrundat'] = self.round_move_carry()

    def change_agecat(self, old, new):
        for i in age_mods[old]:
            self.traits[i] += (age_mods[old][i] * -1)
            self.trace_buys.append('%s: %s' % (i, age_mods[old][i]*-1))
        for i in age_mods[new]:
            self.traits[i] += age_mods[new][i]
            self.trace_buys.append('%s: %s' % (i, age_mods[new][i]))

    
class LoadNpc(Npc):
    def __init__(self, values, user):
        self.id = values['id']
        self.timestamp = values['timestamp']
        self.trace_buys = values['trace_buys']
        self.start_values = values['start_values']
        self.weights = values['weights']
        self.traits = values['traits']
        self.points_left = values['points_left']
        self.skills = values['skills']
        self.hitpoints = values['hitpoints']
        self.move_carry = values['move_carry']
        self.campaign = values['campaign']
        self.notes = values['notes']
        self.name = values['name']

    def toDict(self):
        d = Npc.toDict(self)
        d['name'] = self.name
        d['campaign'] = self.campaign
        d['notes'] = self.notes
        return d
