#!/usr/bin/env python
# coding: utf-8
"""
This script contains function to create PDDL files
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import string
from collections import defaultdict
import operator

class PDDLDomain(object):
    def __init__(self, domain_name, triplets):
        """
        Class to manage the creation of a PDDL file.
        Parameters:
        -----------
        domain_name: string
            string containing the name of the domain
        triplets: array
            list containing triplers of relations in the form: 
            [(subj, rel, obj), (subj, rel, obj), ...]
        init_group: dict
            dictionary containing the group name in the key and 
            the objects as a list in the values
        """
        self.content = '(define (domain {})\n'.format(domain_name)
        self.content += '(:requirements :strips :negative-preconditions)\n\n'
        self.strpred = '(:predicates\n' 
        self.predicates = {}
        self.stract = ''
        self.triplets = triplets
        self.complex_triplets = {}


    def _build_dictionary(self, triplets, other=[]):
        """ Build a dictionary with the objects in triplets, where the
            value of the dictionary is a char.

            Example:
            --------
            triplets [('word1', v1, 'word2'), ('word1', v2, 'word3')]
            output: {'word1': 'a', 'word2': 'b', 'word3': 'c'}
        """
        keys = string.ascii_lowercase
        index = 0
        dic = {}
        drels = {}
        for obj in other:
            dic[obj] = keys[index]
            index += 1
        for s, r, o in triplets:
            if not dic.has_key(s):
                dic[s] = keys[index]
                index += 1
            if not dic.has_key(o):
                dic[o] = keys[index]
                index += 1
            if not drels.has_key(r):
                drels[r] = ''
        return dic, drels
    

    def create_predicates(self):
        """ Create predicates based on groups
        
            Nomeclature:
            ------------
            (:predicates 
              (<obj_1> ?o)
              (<obj_2> ?o)
              (<rel_1> ?x ?y)
              (<rel_2> ?x ?y)
            )
        """
        predicates = ''
        dkeys, drels = self._build_dictionary(self.triplets)
        for obj in dkeys:
            predicates += '  ({} ?o)\n'.format(obj)
        for rel in drels:
            if rel == 'holding':
                predicates += '  ({} ?x ?y)\n'.format('take')
            predicates += '  ({} ?x ?y)\n'.format(rel)
        self.strpred += predicates
        return predicates


    def add_moving_actions(self, sub, verb, obj, prep, place):#
        """Create an action for a subject <sub> that moves <verb> an object <obj>
           to a certain preposition <prep> and place <place>.

           Nomeclature:
           ------------
           ; <person> moves <object> to (<prep_2>) <place>
           (:action move-<sub>-<obj>-<prep_2>-<place_2>
             :parameters (?s ?o ?p) ;s-subject o-object p-place
             :precondition (and (<sub> ?s) (<obj> ?o) (<rel> ?s ?o) (not (<prep> ?o ?p)))
             :effect (and (<prep> ?o ?p))
           )
        
           Example:
           --------
           ; person moves plate to the (on) table
           (:action move-person-plate-on-table
             :parameters (?s ?o ?p)
             :precondition (and (plate ?o) (table ?f)  (take ?s ?o) (not (on ?o ?f)))
             :effect (and (on ?o ?f))
           )
        """
        if self.complex_triplets.has_key(('move', sub, verb, obj, prep, place)):
            logger.warning('Action: move-{}-{}-to-{}-{} already exists!'.format(verb, obj, prep, place))
            return None
        self.complex_triplets[('move', sub, verb, obj, prep, place)] = ''
        logger.info('Creating: action move-{}-to-{}-{}'.format(obj, prep, place))
        action = '(:action move-{}-{}-{}-{}\n'.format(sub, obj, prep, place)
        action += '  :parameters (?s ?o ?p)\n'
        action += '  :precondition (and ({} ?s) ({} ?o) ({} ?p) ({} ?s ?o) (not ({} ?o ?p)))\n'.format(sub, obj, place, verb, prep)
        action += '  :effect (and ({} ?o ?p))\n'.format(prep)
        action += ')\n\n'
        self.stract += action
        return action


    def add_movement_actions(self, sub, prep_s, obj, prep_o, place):
        """ Create the moveobj action to add movement to objects.

           Nomeclature:
           ------------
           ; <sub> <prep> <place> moves <object> <prep> <place>
           (:action moveobj-<sub>-<prep_s>-<obj><prep_o><place>
             :parameters (?s ?o p?) ;s-subject o-object p-place
             :precondition (and (<sub> ?o) (<obj> ?o) (<place> ?p) (<prep_s> ?s ?p) (<prep_o> ?o ?p))
             :effect (and (moving ?s ?o)))
           )
        
           Example:
           --------
           ; turner on frying_pan moves baked_egg in frying_pan
           (:action moveobj-turner-on-baked_egg-in-frying_pan
             :parameters (?s ?o ?p)
             :precondition (and (turner ?s) (baked_egg ?o) (frying_pan ?p) (on ?s ?p) (on ?o ?p))
             :effect (and (moving ?s ?o))
           )
        """
        logger.info('Creating: action moveobj-{}-{}-{}-{}-{}'.format(sub, prep_s, obj, prep_o, place))
        action = '(:action moveobj-{}-{}-{}-{}-{}\n'.format(sub, prep_s, obj, prep_o, place)
        action += '  :parameters (?s ?o ?p)\n'
        action += '  :precondition (and ({} ?s) ({} ?o) ({} ?p) ({} ?s ?p) ({} ?o ?p))\n'.format(sub, obj, place, prep_s, prep_o)
        action += '  :effect (and (moving ?s ?o))\n'
        action += ')\n\n'
        self.stract += action
        return action


    def _putting_action(self, sub, verb, obj, prep, place):#
        """ Create the put action based on handling_actions().

           Nomeclature:
           ------------
           ; <person> puts <object> (<prep>) <place>
           (:action put-<obj>-<prep>-<place>
             :parameters (?s ?o p?) ;s-subject o-object p-place
             :precondition (and (<obj> ?o) (<place> ?p) (on ?o ?p) (take ?s ?o))
             :effect (and (not (take ?s ?o)))
           )
        
           Example:
           --------
           ; person put a plate on the table
           (:action put-plate-on-table
             :parameters (?s ?o ?p)
             :precondition (and (person ?s) (plate ?o) (table ?p) (on ?o ?p) (take ?s ?o))
             :effect (and (not (take ?s ?o)))
           )
        """
        logger.info('Creating: action put-{}-{}-{}'.format(obj, prep, place))
        action = '(:action put-{}-{}-{}\n'.format(obj, prep, place)
        action += '  :parameters (?s ?o ?p)\n'
        action += '  :precondition (and ({} ?o) ({} ?p) ({} ?o ?p) (holding ?s ?o))\n'.format(obj, place, prep)
        action += '  :effect (and (not (holding ?s ?o)) (not (moving ?s ?o)))\n'
        action += ')\n\n'
        return action


    def _taking_action(self, sub, verb, obj, prep, place):#
        """ Create the take action based on handling_actions.

           Nomeclature:
           ------------
           ; <person> takes <object> from (<prep>) <place>
           (:action take-<obj>-<prep>-<place>
             :parameters (?s ?o ?p) ;s-subject o-object p-place
             :precondition (and (<sub> ?s) (<obj> ?o) (<place> ?p) (<prep> ?o ?p) (<verb> ?s ?o))
             :effect (and (not (<prep> ?o ?p)) (take ?s ?o))
           )
        
           Example:
           --------
           ; person takes a plate that is on the table
           (:action take-plate-on-table
             :parameters (?s ?o ?p)
             :precondition (and (person ?s) (plate ?o) (table ?p) (on ?o ?p) (holding ?s ?o))
             :effect (and (not (on ?o ?p)) (take ?s ?o))
           )
        """
        logger.info('Creating: action take-{}-{}-{}'.format(obj, prep, place))
        action = '(:action take-{}-{}-{}\n'.format(obj, prep, place)
        action += '  :parameters (?s ?o ?p)\n'
        #action += '  :precondition (and ({} ?s) ({} ?o) ({} ?p) ({} ?o ?p) ({} ?s ?o))\n'.format(
        #        sub, obj, place, prep, verb)
        #action += '  :effect (and (not ({} ?o ?p)) (take ?s ?o))\n'.format(prep)
        action += '  :precondition (and ({} ?s) ({} ?o) ({} ?p) ({} ?o ?p) (not ({} ?s ?o)))\n'.format(
                sub, obj, place, prep, verb)
        action += '  :effect (and (not ({} ?o ?p)) (holding ?s ?o) (moving ?s ?o))\n'.format(prep)
        action += ')\n\n'
        return action


    def add_handling_action(self, sub, verb, obj, prep, place, mode='all'):#
        """Create (mode='all') actions `take-hold-put` for a subject <sub> 
           doing something <rel> with an object <obj> in/on/above <prep> 
           certain place <place>. 
           
           This method calls `_put` `_hold` and `_take` according to the `mode`.
        """
        if self.complex_triplets.has_key(('take', sub, verb, obj, prep, place)):
            logger.warning('Action: take-{}-{}-{} already exists!'.format(verb, obj, prep, place))
            return None
        self.complex_triplets[('take', sub, verb, obj, prep, place)] = ''
    
        content = ''
        if mode == 'all':
            content = self._taking_action(sub, verb, obj, prep, place)
            #content += self._holding_action(sub, verb, obj, prep, place)
            content += self._putting_action(sub, verb, obj, prep, place)
        elif mode == 'take':
            content = self._taking_action(sub, verb, obj, prep, place)
        elif mode == 'put':
            content = self._putting_action(sub, verb, obj, prep, place)
        #elif mode == 'hold':
        #    content = self._holding_action(sub, verb, obj, prep, place)
        self.stract += content
        return content


    def add_cutting_actions(self, sub, verb, obj, prep, place):#
        """Create a object `<verb>-<obj>`, which is a changed form of <obj>
           by <verb> using <sub> <prep> certain <place>.

           Nomeclature:
           ------------
           ; An <subject> does <verb> an <object> <prep> a <place>
           (:action cut-<sub>-<obj>-<prep>-<place>
             :parameters (?s ?o ?p) ;s-subject o-object p-place
             :precondition (and (<sub> ?s) (<obj> ?o) (<place> ?p) (<verb> ?s ?o) (<prep> ?o ?p))
             :effect (and (not (<obj> ?o) (cut-<obj> ?o))
           )
        
           Example:
           --------
           ; a knife cuts the ham on the cutting_board
           (:action cut-knife-ham-on-table
             :parameters (?s ?o ?p)
             :precondition (and (knife ?s) (ham ?o) (table ?p) (not (cutting ?s ?o)) (on ?o ?p))
             :effect (and (cutting ?s ?o))
           )


        """
        if self.complex_triplets.has_key(('cut', sub, verb, obj, prep, place)):
            logger.warning('Action: cut-{}-{}-{} already exists!'.format(verb, obj, prep, place))
            return None
        self.complex_triplets[('cut', sub, verb, obj, prep, place)] = ''
        logger.info('Creating: action {}-{}-{}-{}'.format(sub, obj, prep, place))
        action = '(:action cut-{}-{}-{}-{}\n'.format(sub, obj, prep, place)
        action += '  :parameters (?s ?o ?p)\n'
        action += '  :precondition (and ({} ?s) ({} ?o) ({} ?p) (not ({} ?s ?o)) ({} ?o ?p))\n'.format(sub, obj, place, verb, prep)
        action += '  :effect (and ({} ?s ?o))\n'.format(verb)
        action += ')\n\n'
        #if not self.predicates.has_key('cut-'+obj):
        #    self.strpred += '  (cut-{} ?o)\n'.format(obj)
        #    self.predicates['cut-'+obj] = ''
        self.stract += action
        return action


    def morphologic_action(self, obj_1, obj_2, preconditions): 
        """ Change the object from object <obj_1> to object <obj_2> 
            when the preconditions <preconditions> holds. Both objects
            belong to the same <group>, and <precondition> is a list of 
            triplets that must hold. 

           Nomeclature:
           ------------
           ; An <object> does <relation> an <object> <prep> a <place>
           (:action <obj_1>-to-<obj_2>
             :parameters ([list of paramenters determined in <precondition>])
             :precondition (and (<obj_1> ?a) [<list of preconditions>])
             :effect (and (not (<obj_1> ?a) (<obj_2> ?a))
           )
        
           Example:
           --------
           ; convert a shell_egg into a boiled_egg having the following list 
           ; of parameters: 
           ; [(bowl, on, table), (pan, on, stove), (shell_egg, in, pan), (bowl, on, table)]
           (:action shell_egg-to-boiled_egg
             :parameters (?a - egg ?b - pan ?c - stove ?d - bowl ?e - table)
             :precondition (and (shell_egg ?a) (on ?b ?c) (in ?a ?b) (on ?d ?e)
             :effect (and (not (shell_egg ?a)) (boiled_egg ?a))
           )
        """
        logger.info('Creating: action {}-to-{}'.format(obj_1, obj_2))
        action = '(:action {}-to-{}\n'.format(obj_1, obj_2)
        action += '  :parameters ('        
        #same_keys = {group: [obj_1, obj_2]}
        dkeys, _ = self._build_dictionary(preconditions, [obj_1, obj_2])
        sorted_keys = sorted([(dkeys[obj], obj) for obj in dkeys])
        for id, obj in sorted_keys:
             action += '?{} '.format(id)
        action = action.rstrip()+')\n'
        action += '  :precondition (and '
        for id, obj in sorted_keys:
            if obj != obj_2:
                action += '({} ?{}) '.format(obj, id)
        for sub, rel, obj in preconditions:
            if rel != 'moving':
                action += '({} ?{} ?{}) '.format(rel, dkeys[sub], dkeys[obj])
        action = action.rstrip()+')\n'
        action += '  :effect (and (not ({} ?{})) ({} ?{}))\n'.format(obj_1, dkeys[obj_1], obj_2, dkeys[obj_2])
        action += ')\n\n'
        self.stract += action
        return action
    

    def save_file(self, path):
        """ Save file at <path> location. """
        self.content += self.strpred+')\n\n'
        self.content += self.stract
        self.content += ')'
        logger.info('Saving file: {}'.format(path))
        with open(path, 'w') as fout:
            fout.write(self.content)
#End of class PDDLDomain

