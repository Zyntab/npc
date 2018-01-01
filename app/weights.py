# -*- coding: utf-8 -*-

hand = {'Högerhänt':14,
        'Vänsterhänt':5,
        'Dubbelhänt':1}


weights = {'Stridis':{'Färdigheter':{'main':40,
                                    'sub':{'Bas':3,
                                           'Skol':1,
                                           'Yrke':5,
                                           'Special_hobb':0}
                                    },
                     'Fysiska_egenskaper':{'main':4,
                                           'sub':{'konst_rörl':1,
                                                  'snabb_uth':1,
                                                  'finm_grovm':1}
                                           },
                     'Mentala_egenskaper':{'main':1,
                                           'sub':{'perc_konc':1,
                                                  'prak_teor':1,
                                                  'log_emo':1}
                                           }
                     },
           'Tänkare':{'Färdigheter':{'main':40,
                                    'sub':{'Bas':3,
                                           'Skol':1,
                                           'Yrke':5,
                                           'Special_hobb':0}
                                    },
                     'Fysiska_egenskaper':{'main':1,
                                           'sub':{'konst_rörl':1,
                                                  'snabb_uth':1,
                                                  'finm_grovm':1}
                                           },
                     'Mentala_egenskaper':{'main':4,
                                           'sub':{'perc_konc':1,
                                                  'prak_teor':1,
                                                  'log_emo':1}
                                           }
                     },
           'Vanlig':{'Färdigheter':{'main':80,
                                    'sub':{'Bas':3,
                                           'Skol':1,
                                           'Yrke':5,
                                           'Special_hobb':0}
                                    },
                     'Fysiska_egenskaper':{'main':5,
                                           'sub':{'konst_rörl':1,
                                                  'snabb_uth':1,
                                                  'finm_grovm':1}
                                           },
                     'Mentala_egenskaper':{'main':5,
                                           'sub':{'perc_konc':1,
                                                  'prak_teor':1,
                                                  'log_emo':1}
                                           }
                     }
           }

fys_ment = {'Stridis':{'Fysisk':1,  # sannolikhet att egenskap okas, den andra minskas
                       'Mental':0
                       },
            'Tänkare':{'Fysisk':0,
                       'Mental':1
                       },
            'Vanlig':{'Fysisk':1,
                      'Mental':1
                      }
            }
