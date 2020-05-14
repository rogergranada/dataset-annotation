#!/usr/bin/env python
# coding: utf-8
"""
This script contains function to create PDDL files
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import string

class PDDLDomainFile(object):
    def __init__(self, domain_name):
        self.content = '(define (domain {})\n'.format(domain_name)
        self.content += '(:requirements :strips :typing :negative-preconditions)\n\n'
    
    def add_positional_actions(self, sub, rel, obj, prep_1, place_1, prep_2, place_2):
        """Create an action for a subject <sub> changing <rel> an object <obj>
           from a certain preposition <prep_1> and place <place_1> to another 
           preposition <prep_2> and place <place_2>.

           Nomeclature:
           ------------
           ; <person> moves <object> from a (<prep_1>) <place> to another (<prep_2>) <place>
           (:action <rel>-<obj>-<prep_1>-<place_1>-to-<prep_2>-<place_2>
             :parameters (?s - <sub> ?o - <obj> i? - <place_1> ?f - <place_2>)
             :precondition (and (<prep_1> ?o ?i) (holding ?s ?o) (<rel> ?s ?o))
             :effect (and (not (<prep_1> ?o ?i) (<prep_2> ?o ?f))
           )
        
           Example:
           --------
           ; person moves shell egg from the (on) table to the (in) pan
           (:action moving-shell_egg-on-table-to-in-pan
             :parameters (?s - person ?o - shell-egg i? - table ?f - pan)
             :precondition (and (on ?o ?i) (holding ?s ?o) (moving ?s ?o))
             :effect (and (not (on ?o ?i) (in ?o ?f))
           )
        """
        logger.info('Creating: action {}-{}-{}-{}-to-{}-{}'.format(rel, obj, prep_1, place_1, prep_2, place_2))
        action = '(:action {}-{}-{}-{}-to-{}-{}\n'.format(rel, obj, prep_1, place_1, prep_2, place_2)
        action += '  :parameters (?s - {} ?o - {} i? - {} ?f - {})\n'.format(sub, obj, place_1, place_2)
        action += '  :precondition (and ({} ?o ?i) (holding ?s ?o) ({} ?s ?o))\n'.format(prep_1, rel)
        action += '  :effect (and (not ({} ?o ?i) ({} ?o ?f))\n'.format(prep_1, prep_2)
        action += ')\n\n'
        self.content += action
        return action


    def add_handling_action(self, sub, rel, obj, prep, place, mode='both'):
        """Create a paired (mode='both') action take-put for a subject <sub> 
           doing something <rel> with an object <obj> in/on/above <prep> 
           certain place <place>. 

           Nomeclature:
           ------------
           ; <person> take <object> from a (<pos_1>) <place>
           (:action take-<obj>-<prep>-<place>
             :parameters (?s - <sub> ?o - <obj> p? - <place>)
             :precondition (and (<prep> ?o ?p))
             :effect (and (not (<prep> ?o ?p) (<rel> ?s ?o))
           )
        
           Example:
           --------
           ; person takes a shell egg that is on the table
           (:action take-shell_egg-on-table
             :parameters (?s - person ?o - shell-egg p? - table)
             :precondition (and (on ?o ?p))
             :effect (and (not (on ?o ?p) (holding ?s ?o))
           )
        """
        logger.info('Creating: action take-{}-{}-{}'.format(obj, prep, place))
        take = '(:action take-{}-{}-{}\n'.format(obj, prep, place)
        take += '  :parameters (?s - {} ?o - {} p? - {})\n'.format(sub, obj, place)
        take += '  :precondition (and ({} ?o ?p))\n'.format(prep)
        take += '  :effect (and (not ({} ?o ?p) ({} ?s ?o))\n'.format(prep, rel)
        take += ')\n\n'

        put = '(:action put-{}-{}-{}\n'.format(obj, prep, place)
        put += '  :parameters (?s - {} ?o - {} p? - {})\n'.format(sub, obj, place)
        put += '  :precondition (and ({} ?s ?o))\n'.format(rel)
        put += '  :effect (and (not ({} ?s ?o) ({} ?o ?p))\n'.format(rel, prep)
        put += ')\n\n'
    
        content = ''
        if mode == 'both':
            content = take+put
        elif mode == 'take':
            content = take
        elif mode == 'put':
            content = put
        self.content += content
        return content
            

    def add_manipulation_actions(sub, rel, obj_1, obj_2, prep, place):
        """Create a modified object <obj>, which was modified by the 
           application <rel> of another object <obj_2> in/on/above 
           <prep> certain place <place> by subject <sub>.

           Nomeclature:
           ------------
           ; An <object> does <relation> an <object> <prep> a <place>
           (:action <rel>-<obj_1>-<prep>-<place>
             :parameters (?s - <sub> ?o - <obj_1> ?b - <obj_2> p? - <place>)
             :precondition (and (<prep> ?o ?p) (on ?b ?o) (holding ?s ?b))
             :effect (and (not (on ?b ?o) (<rel>-<obj_1> ?o))
           )
        
           Example:
           --------
           ; a knife cuts the ham on the cutting_board
           (:action cutting-ham-on-cutting_board
             :parameters (?s - person ?o - ham ?b - knife p? - cutting_board)
             :precondition (and (on ?o ?p) (on ?b ?o) (holding ?s ?b))
             :effect (and (not (on ?b ?o) (cutting-ham ?o))
           )
        """
        logger.info('Creating: action {}-{}-{}-{}'.format(rel, obj_1, prep, place))
        action = '(:action {}-{}-{}-{}\n'.format(rel, obj_1, prep, place)
        action += '  :parameters (?s - {} ?o - {} ?b - {} p? - {})\n'.format(sub, obj_1, obj_2, place)
        action += '  :precondition (and ({} ?o ?p) (on ?b ?o) (holding ?s ?b))\n'.format(prep)
        action += '  :effect (and (not (on ?b ?o) ({}-{} ?o))\n'.format(rel, obj_1)
        action += ')\n\n'
        self.content += action
        return action


    def _generate_keys(self, obj_1, obj_2, triplets):
        """ Generate unique keys for objects """
        keys = string.ascii_lowercase
        # both are the same group: 'a'
        dkeys = {obj_1: keys[0], obj_2: keys[0]}
        index = 1
        for sub, rel, obj in triplets:
            if not dkeys.has_key(sub):
                dkeys[sub] = keys[index]
                index += 1
            if not dkeys.has_key(obj):
                dkeys[obj] = keys[index]
                index += 1
        return dkeys

    
    def change_object(self, obj_1, obj_2, group, preconditions): 
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
             :effect (and (not (shell_egg ?a) (boiled_egg ?a))
           )
        """
        logger.info('Creating: action {}-to-{}'.format(obj_1, obj_2))
        action = '(:action {}-to-{}\n'.format(obj_1, obj_2)
        action += '  :parameters (?a - {} '.format(group)

        dkeys = self._generate_keys(obj_1, obj_2, preconditions)
        print dkeys
        sorted_keys = sorted([(dkeys[obj], obj) for obj in dkeys])
        for id, obj in sorted_keys:
            if not obj == obj_1 and not obj == obj_2:
                action += '?{} - {} '.format(id, obj)
        action = action.rstrip()+')\n'
        action += '  :precondition (and ({} ?{}) '.format(obj_1, dkeys[obj_1])
        for sub, rel, obj in preconditions:
            action += '({} ?{} ?{}) '.format(rel, dkeys[sub], dkeys[obj])
        action = action.rstrip()+')\n'
        action += '  :effect (and (not ({} ?{}) ({} ?{}))\n'.format(obj_1, dkeys[obj_1], obj_2, dkeys[obj_2])
        action += ')\n\n'
        self.content += action
        return action


    def save_file(self, path):
        """ Save file at <path> location. """
        logger.info('Saving file: {}'.format(path))
        with open(path, 'w') as fout:
            fout.write(self.content)
#End of PDDLFile class




























