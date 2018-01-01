# -*- coding: utf-8 -*-

agetypes = {'Människa':{'Ung': (15,24),
                       'Mogen': (25,38),
                       'Medel': (39,55),
                       'Gammal': (56,65),
                       'Åldring': (66,85)},
           'Gôr':     {'Ung': (15,24),
                       'Mogen': (25,75),
                       'Medel': (76,110),
                       'Gammal': (111,150),
                       'Åldring': (151,250)}
         }

agecats = {'Människa':{'Ung':24,
                        'Mogen':38,
                        'Medel':55,
                        'Gammal':65},
            'Gôr':     {'Ung':24,
                        'Mogen':75,
                        'Medel':110,
                        'Gammal':150}
        }

age_mods = {'Ung':{'Emotionell':-1,
                   'Koncentration':-1,
                   'Konstitution':1,
                   'Rörlighet':1,
                   'Snabbhet':1},
            'Mogen':{},
            'Medel':{'Emotionell':1,
                     'Finmotorik':-1,
                     'Konstitution':-1,
                     'Perception':-1,
                     'Rörlighet':-1,
                     'Snabbhet':-1,
                     'Uthållighet':-1},
            'Gammal':{'Emotionell':2,
                      'Finmotorik':-1,
                      'Grovmotorik':-1,
                      'Koncentration':-1,
                      'Konstitution':-2,
                      'Perception':-2,
                      'Rörlighet':-2,
                      'Snabbhet':-2,
                      'Uthållighet':-2,
                      'Syn':-1,
                      'Hörsel':-1,
                      'Lukt':-1,
                      'Känsel':-1,
                      'Smak':-1},
            'Åldring':{'Emotionell':2,
                       'Finmotorik':-2,
                       'Grovmotorik':-1,
                       'Koncentration':-1,
                       'Konstitution':-3,
                       'Logisk':-1,
                       'Perception':-2,
                       'Rörlighet':-3,
                       'Snabbhet':-3,
                       'Uthållighet':-3,
                       'Syn':-2,
                       'Hörsel':-2,
                       'Lukt':-2,
                       'Känsel':-2,
                       'Smak':-2}
        }

gender_mods = {'Människa':{'Man':{'Konstitution':1,
                                 'Snabbhet':1,
                                 'Finmotorik':-1,
                                 'Praktisk':1},
                          'Kvinna':{'Rörlighet':1,
                                    'Emotionell':1}
                          },
              'Gôr':{'Man':{'Koncentration':-1,
                            'Emotionell':-1},
                     'Kvinna':{'Konstitution':-1,
                               'Uthållighet':-1,
                               'Finmotorik':-1,
                               'Teoretisk':1}
                     }
              }

heights = {'Människa':{'Man':{'Kort':(150,163),
                              'Medel':(163,177),
                              'Lång':(177,200)
                              },
                       'Kvinna':{'Kort':(140,153),
                                 'Medel':(153,167),
                                 'Lång':(167,180)
                                 }
                       },
           'Gôr':{'Man':{'Kort':(120,133),
                         'Medel':(133,147),
                         'Lång':(147,160)
                         },
                  'Kvinna':{'Kort':(110,123),
                            'Medel':(123,137),
                            'Lång':(137,150)
                            }
                  }
           }

race_mods = {'Människa':{'Konstitution':-1,
                         'Snabbhet':-1,
                         'Praktisk':-1},
             'Gôr':     {'Konstitution':1,
                         'Rörlighet':-1,
                         'Snabbhet':-1,
                         'Uthållighet':1,
                         'Koncentration':1,
                         'Praktisk':1,
                         'Syn':-1,
                         'Hörsel':-1,
                         'Lukt':1,
                         'Känsel':-1}
             }

