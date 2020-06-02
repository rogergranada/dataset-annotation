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

class PDDLDomain(object):
    def __init__(self, domain_name, triplets, init_group=None):
        """

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
        self.triplets = triplets

        self.objects = {}
        self.relations = {}
        self.complex_triplets = {}
        self._objects_relations()

    def _objects_relations(self):
        keys = string.ascii_lowercase
        index = 0
        for s, r, o in self.triplets:
            if not self.objects.has_key(s):
                self.objects[s] = keys[index]
                index += 1
            if not self.objects.has_key(o):
                self.objects[o] = keys[index]
                index += 1
            if not self.relations.has_key(r):
                self.relations[r] = ''
        return self.objects, self.relations
    

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
        predicates = '(:predicates\n'
        for obj in self.objects:
            predicates += '  ({} ?o)\n'.format(obj)
        for rel in self.relations:
            if rel == 'holding':
                predicates += '  ({} ?x ?y)\n'.format('take')
            predicates += '  ({} ?x ?y)\n'.format(rel)
        predicates += ')\n\n'
        self.content += predicates
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

       
        if self.complex_triplets.has_key(('move', sub, verb, obj, prep, place)):
            logger.warning('Action: move-{}-{}-to-{}-{} already exists!'.format(verb, obj, prep, place))
            return None
        self.complex_triplets[('move', sub, verb, obj, prep, place)] = ''
        logger.info('Creating: action {}-{}-to-{}-{}'.format(verb, obj, prep, place))
        action = '(:action move-{}-{}-{}-{}\n'.format(sub, obj, prep, place)
        action += '  :parameters (?{} ?{} ?{})\n'.format(self.objects[sub], self.objects[obj], self.objects[place])
        action += '  :precondition (and ({} ?{}) ({} ?{})  (take ?{} ?{}) (not ({} ?{} ?{})))\n'.format(
                  obj, self.objects[obj], place, self.objects[place], self.objects[sub], self.objects[obj], 
                  prep, self.objects[obj], self.objects[place])
        action += '  :effect (and ({} ?{} ?{}))\n'.format(prep, self.objects[obj], self.objects[place])
        action += ')\n\n'
        self.content += action
        """
        if self.complex_triplets.has_key(('move', sub, verb, obj, prep, place)):
            logger.warning('Action: move-{}-{}-to-{}-{} already exists!'.format(verb, obj, prep, place))
            return None
        self.complex_triplets[('move', sub, verb, obj, prep, place)] = ''
        logger.info('Creating: action {}-{}-to-{}-{}'.format(verb, obj, prep, place))
        action = '(:action move-{}-{}-{}-{}\n'.format(sub, obj, prep, place)
        action += '  :parameters (?s ?o ?p)\n'
        action += '  :precondition (and ({} ?o) ({} ?p) (take ?s ?o) (not ({} ?o ?p)))\n'.format(obj, place, prep)
        action += '  :effect (and ({} ?o ?p))\n'.format(prep)
        action += ')\n\n'
        self.content += action
        return action

    def _putting_action(self, sub, verb, obj, prep, place):#
        """ Create the put action based on handling_actions."""
        logger.info('Creating: action take-{}-{}-{}'.format(obj, prep, place))
        action = '(:action put-{}-{}-{}\n'.format(obj, prep, place)
        action += '  :parameters (?{} ?{} ?{})\n'.format(self.objects[sub], self.objects[obj], self.objects[place])
        action += '  :precondition (and ({} ?{}) ({} ?{}) ({} ?{} ?{}) (take ?{} ?{}))\n'.format(obj, self.objects[obj], 
                place, self.objects[place], prep, self.objects[obj], self.objects[place], self.objects[sub], self.objects[obj])
        action += '  :effect (and (not (take ?{} ?{})))\n'.format(self.objects[sub], self.objects[obj])
        action += ')\n\n'
        return action

    def _taking_action(self, sub, verb, obj, prep, place):#
        """ Create the take action based on handling_actions."""
        logger.info('Creating: action take-{}-{}-{}'.format(obj, prep, place))
        action = '(:action take-{}-{}-{}\n'.format(obj, prep, place)
        action += '  :parameters (?{} ?{} ?{})\n'.format(self.objects[sub], self.objects[obj], self.objects[place])
        action += '  :precondition (and ({} ?{}) ({} ?{}) ({} ?{}) ({} ?{} ?{}) ({} ?{} ?{}))\n'.format(
                sub, self.objects[sub], obj, self.objects[obj], place, self.objects[place], 
                prep, self.objects[obj], self.objects[place], verb, self.objects[sub], self.objects[obj])
        action += '  :effect (and (not ({} ?{} ?{})) (take ?{} ?{}))\n'.format(
                prep, self.objects[obj], self.objects[place], self.objects[sub], self.objects[obj])
        action += ')\n\n'
        return action


    def add_handling_action(self, sub, verb, obj, prep, place, mode='both'):#
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
           (:action take-shell-egg-from-table
             :parameters (?s - person ?o - egg ?p - table)
             :precondition (and (person ?s) (shell-egg ?o) (table ?p) (on ?o ?p) (holding ?s ?o))
             :effect (and (not (on ?o ?p) (take ?s ?o)))
           )
        """
        if self.complex_triplets.has_key(('take', sub, verb, obj, prep, place)):
            logger.warning('Action: take-{}-{}-{} already exists!'.format(verb, obj, prep, place))
            return None
        self.complex_triplets[('take', sub, verb, obj, prep, place)] = ''
        take = self._taking_action(sub, verb, obj, prep, place)
        put = self._putting_action(sub, verb, obj, prep, place)
    
        content = ''
        if mode == 'both':
            content = take+put
        elif mode == 'take':
            content = take
        elif mode == 'put':
            content = put
        self.content += content
        return content

    def add_cutting_actions(self, sub, verb, obj, prep, place):#
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
           (:action cut-knife-egg-on-cutting-board
             :parameters (?o - egg ?s - knife ?p - cutting-board)
             :precondition (and (hard-boiled-egg ?o) (cutting ?s ?o) (on ?o ?p))
             :effect (and (not (hard-boiled-egg ?o)) (cut-hard-boiled-egg ?o))
           )
        """
        if self.complex_triplets.has_key(('cut', sub, verb, obj, prep, place)):
            logger.warning('Action: cut-{}-{}-{} already exists!'.format(verb, obj, prep, place))
            return None
        self.complex_triplets[('cut', sub, verb, obj, prep, place)] = ''
        logger.info('Creating: action {}-{}-{}-{}'.format(sub, obj, prep, place))
        action = '(:action cut-{}-{}-{}-{}\n'.format(sub, obj, prep, place)
        action += '  :parameters (?{} ?{} ?{})\n'.format(self.objects[sub], self.objects[obj], self.objects[place])
        action += '  :precondition (and ({} ?{}) ({} ?{} ?{}) ({} ?{} ?{}))\n'.format(sub, self.objects[sub], 
                  verb, self.objects[sub], self.objects[obj], prep, self.objects[obj], self.objects[place])
        action += '  :effect (and (not ({} ?{}) (cut-{} ?{}))\n'.format(obj, self.objects[obj], obj, self.objects[obj])
        action += ')\n\n'
        self.content += action
        return action

    def _filter_keys_by_triplets(self, triplets, other=None):
        dic = {}
        for obj in other:
            dic[obj] = self.objects[obj]

        for s, r, o in triplets:
            if self.objects.has_key(s):
                dic[s] = self.objects[s]
            if self.objects.has_key(o):
                dic[o] = self.objects[o]
        return dic

    def morphologic_action(self, obj_1, obj_2, group, preconditions): 
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
        action += '  :parameters ('        
        #same_keys = {group: [obj_1, obj_2]}
        dkeys = self._filter_keys_by_triplets(preconditions, [obj_1, obj_2])
        sorted_keys = sorted([(dkeys[obj], obj) for obj in dkeys])
        for id, obj in sorted_keys:
        #    if obj != obj_1 and obj != obj_2:
             action += '?{} '.format(id)
        action = action.rstrip()+')\n'
        action += '  :precondition (and '
        for id, obj in sorted_keys:
            if obj != obj_2:
                action += '({} ?{}) '.format(obj, id)
        for sub, rel, obj in preconditions:
            if rel == 'holding':
                action += '(take ?{} ?{}) '.format(dkeys[sub], dkeys[obj])
            else:
                action += '({} ?{} ?{}) '.format(rel, dkeys[sub], dkeys[obj])
        action = action.rstrip()+')\n'
        action += '  :effect (and (not ({} ?{})) ({} ?{}))\n'.format(obj_1, dkeys[obj_1], obj_2, dkeys[obj_2])
        action += ')\n\n'
        self.content += action
        return action
    

    def save_file(self, path):
        """ Save file at <path> location. """
        self.content += ')'
        logger.info('Saving file: {}'.format(path))
        with open(path, 'w') as fout:
            fout.write(self.content)
#End of class PDDLDomain


class PDDLDomainFile(object):
    def __init__(self, domain_name, triplets, init_group=None):
        """

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
        self.triplets = triplets
        self.init_group = init_group
        self.groups, self.triplets_groups = self._group_relations()
        self.objs_ids = self._generate_keys()
        self.group = self._invert_dic()
        self.complex_triplets = {}
        self.elements = self._key_elements()
    
        self.content = '(define (domain {})\n'.format(domain_name)
        self.content += '(:requirements :strips :typing :negative-preconditions)\n\n'

    def _invert_dic(self):
        dic = {}
        for group in self.init_group:
            for obj in self.init_group[group]:
                dic[obj] = group
        for sub, rel, obj in self.triplets:
            if not dic.has_key(sub):
                dic[sub] = sub
            if not dic.has_key(obj):
                dic[obj] = obj
        return dic

    def _key_elements(self):
        dic = {}
        for sub, rel, obj in self.triplets:
            if self.objs_ids.has_key(sub):
                dic[sub] = self.objs_ids[sub]
            if self.objs_ids.has_key(obj):
                dic[obj] = self.objs_ids[obj]
            if not self.rels.has_key(rel):
                self.rels[rel] = ''
        return dic

    def _group_relations(self):
        """ Create groups of subjects and objects that use the same predicate.

            dic ={<rel>'_sub': [<subject_1>, <subject_2>, ... <subject_n>],
                  <rel>'_obj': [<object_1>, <object_2>, ... <object_n>]}
        """ 
        dic = defaultdict(list)
        for sub, rel, obj in self.triplets:
            dic[rel+'_sub'].append(sub)
            dic[rel+'_obj'].append(obj)
        for key in dic:
            dic[key] = set(dic[key])
        triplets_group = []
        for key in dic:
            if key.endswith('_sub'):
                rel = key.split('_')[0]
                triplets_group.append((key, rel, rel+'_obj')) 
        return dic, triplets_group


    def _generate_keys(self):
        """ Generate unique keys for objects """
        keys = string.ascii_lowercase
        dkeys = {}
        index = 0
        for group in self.init_group:
            dkeys[group] = keys[index]
            for obj in self.init_group[group]:
                dkeys[obj] = keys[index]
            index += 1
        for sub, rel, obj in self.triplets:
            if not dkeys.has_key(sub):
                dkeys[sub] = keys[index]
                index += 1
            if not dkeys.has_key(obj):
                dkeys[obj] = keys[index]
                index += 1
        for sub, rel, obj in self.triplets_groups:
            if not dkeys.has_key(sub):
                dkeys[sub] = keys[index]
                index += 1
            if not dkeys.has_key(obj):
                dkeys[obj] = keys[index]
                index += 1
        return dkeys


    def _generate_keys_commented(self, obj_1, obj_2, triplets):
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


    def create_types(self):
        """ Group elements as and create `types` in PDDL 

           Nomeclature:
           ------------
           (:types
             <obj_1> <obj_2> <obj_3> <obj_4> - <group_1> 
             <obj_3> <obj_4> <obj_5> <obj_6> - <group_2> 
           )
        """
        types = '(:types\n'
        print '>', self.groups
        print self.group
        for group in sorted(self.groups):
            types += '  '
            dic = {}
            for element in sorted(self.groups[group]):
                obj = self.group[element]
                if not dic.has_key(obj):
                    types += '{} '.format(obj)
                    dic[obj] = ''
            types = '{} - {}\n'.format(types.strip(), group)
        types += ')\n\n'
        self.content += types
        return types


    def create_predicates(self):
        """ Create predicates based on groups
        
            Nomeclature:
            ------------
            (:predicates 
              (<rel_1> ?<key_1> - <group_1> ?<key_2> - <group_2>)
              (<rel_2> ?<key_3> - <group_3> ?<key_4> - <group_4>)
              (<obj_1> ?<group_id> - <group>)
            )
        """
        predicates = '(:predicates\n'
        #print self.triplets_groups
        for obj in self.objs_ids:
            predicates += '  ({} ?o)\n'.format(obj)
        for rel in self.rels:
            if rel == 'holding':
                predicates += '  ({} ?x ?y)\n'.format('take', rel)
        #print '1:',self.init_group
        #for group in self.init_group:
        #    predicates += '  ({} ?{} - {} ?{} - {})\n'.format(rel, self.objs_ids[sub], sub, self.objs_ids[obj], obj)
        #print '2:',predicates
        '''
        print self.group
        for obj in self.elements:
            if self.group.has_key(obj) and self.group[obj] != obj:
                predicates += '  ({} ?{} - {})\n'.format(obj, self.objs_ids[obj], self.group[obj])
            else:
                predicates += '  ({} ?{})\n'.format(obj, self.objs_ids[obj])
        #print '3:',predicates
        '''
        predicates += ')\n\n'
        self.content += predicates
        return predicates


    def _create_predicates(self):
        """ Create predicates based on groups
        
            Nomeclature:
            ------------
            (:predicates 
              (<rel_1> ?<key_1> - <group_1> ?<key_2> - <group_2>)
              (<rel_2> ?<key_3> - <group_3> ?<key_4> - <group_4>)
              (<obj_1> ?<group_id> - <group>)
            )
        """
        predicates = '(:predicates\n'
        #print self.triplets_groups
        for sub, rel, obj in self.triplets_groups:
            predicates += '  ({} ?{} - {} ?{} - {})\n'.format(rel, self.objs_ids[sub], sub, self.objs_ids[obj], obj)
            if rel == 'holding':
                predicates += '  ({} ?{} - {} ?{} - {})\n'.format('take', self.objs_ids[sub], sub, self.objs_ids[obj], obj)
        #print '1:',self.init_group
        #for group in self.init_group:
        #    predicates += '  ({} ?{} - {} ?{} - {})\n'.format(rel, self.objs_ids[sub], sub, self.objs_ids[obj], obj)
        #print '2:',predicates
        print self.group
        for obj in self.elements:
            if self.group.has_key(obj) and self.group[obj] != obj:
                predicates += '  ({} ?{} - {})\n'.format(obj, self.objs_ids[obj], self.group[obj])
            else:
                predicates += '  ({} ?{})\n'.format(obj, self.objs_ids[obj])
        #print '3:',predicates
        predicates += ')\n\n'
        self.content += predicates
        return predicates


    def add_moving_actions(self, sub, verb, obj, prep, place):#
        """Create an action for a subject <sub> that moves <verb> an object <obj>
           to a certain preposition <prep> and place <place>.

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
           ; person moves shell egg to the (on) plate
           (:action move-shell-egg-to-on-plate
             :parameters (?a - person ?b - egg ?c - plate)
             :precondition (and (hard-boiled-egg ?b) (plate ?c) 
                                (take ?a ?b) (not (on ?b ?c)))
             :effect (and (on ?b ?c))
           )
        """
        if self.complex_triplets.has_key(('move', sub, verb, obj, prep, place)):
            logger.warning('Action: move-{}-{}-to-{}-{} already exists!'.format(verb, obj, prep, place))
            return None
        self.complex_triplets[('move', sub, verb, obj, prep, place)] = ''
        logger.info('Creating: action {}-{}-to-{}-{}'.format(verb, obj, prep, place))
        action = '(:action move-{}-{}-{}-{}\n'.format(sub, obj, prep, place)
        action += '  :parameters (?{} - {} ?{} - {} ?{} - {})\n'.format(self.objs_ids[sub], sub, self.objs_ids[obj], obj, self.objs_ids[place], place)
        action += '  :precondition (and ({} ?{}) ({} ?{})  (take ?{} ?{}) (not ({} ?{} ?{})))\n'.format(obj, self.objs_ids[obj], place, self.objs_ids[place], self.objs_ids[sub], self.objs_ids[obj], prep, self.objs_ids[obj], self.objs_ids[place])
        action += '  :effect (and ({} ?{} ?{}))\n'.format(prep, self.objs_ids[obj], self.objs_ids[place])
        action += ')\n\n'
        self.content += action
        return action


    def add_handling_action(self, sub, verb, obj, prep, place, mode='both'):#
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
           (:action take-shell-egg-from-table
             :parameters (?s - person ?o - egg ?p - table)
             :precondition (and (person ?s) (shell-egg ?o) (table ?p) (on ?o ?p) (holding ?s ?o))
             :effect (and (not (on ?o ?p) (take ?s ?o)))
           )
        """
        if self.complex_triplets.has_key(('take', sub, verb, obj, prep, place)):
            logger.warning('Action: take-{}-{}-{} already exists!'.format(verb, obj, prep, place))
            return None
        self.complex_triplets[('take', sub, verb, obj, prep, place)] = ''
        #use grouped <obj>
        gobj = self.group[obj]
        logger.info('Creating: action take-{}-{}-{}'.format(gobj, prep, place))
        take = '(:action take-{}-{}-{}\n'.format(obj, prep, place)
        take += '  :parameters (?{} - {} ?{} - {} ?{} - {})\n'.format(self.objs_ids[sub], sub, self.objs_ids[gobj], gobj, self.objs_ids[place], place)
        take += '  :precondition (and ({} ?{}) ({} ?{}) ({} ?{}) ({} ?{} ?{}) ({} ?{} ?{}))\n'.format(sub, self.objs_ids[sub], obj, self.objs_ids[obj], place, self.objs_ids[place], prep, self.objs_ids[obj], self.objs_ids[place], verb, self.objs_ids[sub], self.objs_ids[obj])
        take += '  :effect (and (not ({} ?{} ?{})) (take ?{} ?{}))\n'.format(prep, self.objs_ids[obj], self.objs_ids[place], self.objs_ids[sub], self.objs_ids[obj])
        take += ')\n\n'

        put = '(:action put-{}-{}-{}\n'.format(obj, prep, place)
        put += '  :parameters (?{} - {} ?{} - {} ?{} - {})\n'.format(self.objs_ids[sub], sub, self.objs_ids[obj], obj, self.objs_ids[place], place)
        put += '  :precondition (and ({} ?{}) ({} ?{}) ({} ?{}) ({} ?{} ?{}) (take ?{} ?{}))\n'.format(sub, self.objs_ids[sub], obj, self.objs_ids[obj], place, self.objs_ids[place], prep, self.objs_ids[obj], self.objs_ids[place], self.objs_ids[sub], self.objs_ids[obj])
        put += '  :effect (and (not (take ?{} ?{})))\n'.format(self.objs_ids[sub], self.objs_ids[obj])
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
            

    def add_manipulation_actions(sub, verb, obj, prep, place):#
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
           (:action cut-knife-egg-on-cutting-board
             :parameters (?o - egg ?s - knife ?p - cutting-board)
             :precondition (and (hard-boiled-egg ?o) (cutting ?s ?o) (on ?o ?p))
             :effect (and (not (hard-boiled-egg ?o)) (cut-hard-boiled-egg ?o))
           )
        """
        if self.complex_triplets.has_key(('cut', sub, verb, obj, prep, place)):
            logger.warning('Action: cut-{}-{}-{} already exists!'.format(verb, obj, prep, place))
            return None
        self.complex_triplets[('cut', sub, verb, obj, prep, place)] = ''
        #use grouped <obj>
        gobj = self.group[obj]
        logger.info('Creating: action {}-{}-{}-{}'.format(sub, gobj, prep, place))
        action = '(:action cut-{}-{}-{}-{}\n'.format(sub, gobj, prep, place)
        action += '  :parameters (?{} - {} ?{} - {} ?{} - {})\n'.format(self.objs_ids[sub], sub, self.objs_ids[gobj], gobj, self.objs_ids[place], place)
        action += '  :precondition (and ({} ?{}) ({} ?{} ?{}) ({} ?{} ?{}))\n'.format(sub, self.objs_ids[sub], verb, self.objs_ids[sub], self.objs_ids[obj], prep, self.objs_ids[obj], self.objs_ids[place])
        action += '  :effect (and (not ({} ?{}) (cut-{} ?{}))\n'.format(obj, self.objs_ids[obj], obj, self.objs_ids[obj])
        action += ')\n\n'
        self.content += action
        return action


    def _filter_keys_by_triplets(self, triplets, other=None):
        dic = {}
        for obj in other:
            dic[obj] = self.objs_ids[obj]

        for s, r, o in triplets:
            if self.objs_ids.has_key(s):
                dic[s] = self.objs_ids[s]
            if self.objs_ids.has_key(o):
                dic[o] = self.objs_ids[o]
        return dic

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
        
        same_keys = {group: [obj_1, obj_2]}
        dkeys = self._filter_keys_by_triplets(preconditions, [obj_1, obj_2])
        sorted_keys = sorted([(dkeys[obj], obj) for obj in dkeys])
        for id, obj in sorted_keys:
            if obj != obj_1 and obj != obj_2:
                action += '?{} - {} '.format(id, obj)
        action = action.rstrip()+')\n'
        action += '  :precondition (and ({} ?{}) '.format(obj_1, dkeys[obj_1])
        for sub, rel, obj in preconditions:
            action += '({} ?{} ?{}) '.format(rel, dkeys[sub], dkeys[obj])
        action = action.rstrip()+')\n'
        action += '  :effect (and (not ({} ?{})) ({} ?{}))\n'.format(obj_1, dkeys[obj_1], obj_2, dkeys[obj_2])
        action += ')\n\n'
        self.content += action
        return action
    

    def save_file(self, path):
        """ Save file at <path> location. """
        self.content += ')'
        logger.info('Saving file: {}'.format(path))
        with open(path, 'w') as fout:
            fout.write(self.content)
#End of PDDLFile class




























