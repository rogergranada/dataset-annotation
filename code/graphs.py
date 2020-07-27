#!/usr/bin/env python
# coding: utf-8
"""
This script contains a class to deal with graphs
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import string
import networkx as nx
import graph

class RelationsGraph(object):
    def __init__(self, init_state=None):
        self.graph = graph.Graph()
        self.triplets = None
        if init_state:
            self.add_triplets(init_state)


    def add_triplets(self, triplets):
        """ Add triplets into the Multi Direct Graph
            
        Parameters:
        -----------
        triplets: 2D-array
            array containing [[subject, relation, object], [...]]
        """ 
        for sub, rel, obj in triplets:
            self.graph.add_node(sub)
            self.graph.add_node(obj)
            self.graph.add_edge(sub, obj, rel)


    def allow_movement(self, movement_verb, relations):
        """ Yield relations where the object can be moved.

        Parameters:
        -----------
        movement_verb: string
            the verb representing the action taking place (e.g. moving).
        relations: array
            a list containing prepositions such as ['in', 'on', 'above'].

        Example:
        --------
        A <turner> can <move> a <baked_egg> that is <in> the <frying_pan> iff
        the <turner> in <on> the <frying_pan>.
        The output of the allow_movement() for this example is:
        (turner, on, baked_egg, in, frying_pan) 
        """
        for sub, obj, verb in self.graph:
            if verb == movement_verb:
                dadj_s = self.graph.adjacency(sub)
                dadj_o = self.graph.adjacency(obj)
                places = set(dadj_s).intersection(set(dadj_o))
                if places:
                    for place in places:
                        for prep_s in dadj_s[place]:
                            for prep_o in dadj_o[place]:
                                if prep_s in relations and prep_o in relations:
                                    yield sub, prep_s, obj, prep_o, place  


    def handling_relations(self, handle_verb, relations):
        """ Yield handling relations.
        
        Handling relations are relations containing the movement of an 
        object that is in/on/above a place. 

        Parameters:
        -----------
        handle_verb: string
            the verb representing the action taking place (e.g. holding or cutting).
        relations: array
            a list containing prepositions such as ['in', 'on', 'above'].

        Example:
        --------
        A <person> can <hold> a <shell_egg> that is <on> the <table> before
        moving it to some place.
        The output of the handling_relations() for this example is:
        (person, holding, shell_egg, on table) 
        """
        for sub, obj, verb in self.graph:
            if verb == handle_verb:
                dadj = self.graph.adjacency(obj)
                if dadj:
                    for obj2 in dadj:
                        for prep in dadj[obj2]:
                            if prep in relations:
                                yield (sub, verb, obj, prep, obj2)


    def displacement_relations(self, relations):
        """ Yield displacement relations between nodes. 

        A displacement relation occurs when an object can be transferred 
        between two places.

        Parameters:
        -----------
        relations: array
            a list containing prepositions such as ['in', 'on', 'above'].

        Example:
        --------
        A <shell_egg> can be moved from <on> table to <in> pan. In the
        graph, it is represented as two edges from the same node containing
        two prepositions in <relations>.
        The output of the moving_position() for this example is:
        (shell_egg, on, table, in, pan)
        """
        for sub, obj, verb in self.graph:
            if verb == handle_verb:
                dadj = self.graph.adjacency(obj)
                if dadj:
                    for obj2 in dadj:
                        for prep in dadj[obj2]:
                            if prep in relations:
                                yield (sub, verb, obj, prep, obj2)



    def has_connection(node1, node2):
        return self.graph.has_edge(node1, node2)

    def save_file(self, path):
        """ Save file at <path> location. 

        Parameters:
        -----------
        path: string
            path to save the file
        """
        logger.info('Saving file: {}'.format(path))
        with open(path, 'w') as fout:
            fout.write(self.graph)
#End of PDDLFile class



class RelationsGraphNx(object):
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.triplets = None


    def add_triplets(self, triplets):
        """ Add triplets into the Multi Direct Graph
            
        Parameters:
        -----------
        triplets: 2D-array
            array containing [[subject, relation, object], [...]]
        """ 
        for sub, rel, obj in triplets:
            self.graph.add_node(sub)
            self.graph.add_node(obj)
            self.graph.add_edge(sub, obj, key=rel)

    def displacement_relations(self, relations):
        """ Yield displacement relations between nodes. 

        A displacement relation occurs when an object can be transferred 
        between two places.

        Parameters:
        -----------
        relations: array
            a list containing prepositions such as ['in', 'on', 'above'].

        Example:
        --------
        A <shell_egg> can be moved from <on> table to <in> pan. In the
        graph, it is represented as two edges from the same node containing
        two prepositions in <relations>.
        The output of the moving_position() for this example is:
        (shell_egg, on, table, in, pan)
        """
        for sub, objs in self.graph.adjacency():
            for obj, props in objs.items():
                for prop in props:
                    for obj1, props1 in objs.items():
                        if obj != obj1:
                            for prop1 in props1:
                                if prop in relations and prop1 in relations:
                                    # shell_egg (on) table (in) pan
                                    yield (sub, prop, obj, prop1, obj1)

    def handling_relations(self, handle_verb, relations):
        """ Yield handling relations.
        
        Handling relations are relations containing the movement of an 
        object that is in/on/above a place. 

        Parameters:
        -----------
        handle_verb: string
            the verb representing the action taking place (e.g. holding or cutting).
        relations: array
            a list containing prepositions such as ['in', 'on', 'above'].

        Example:
        --------
        A <person> can <hold> a <shell_egg> that is <on> the <table> before
        moving it to some place.
        The output of the handling_relations() for this example is:
        (person, holding, shell_egg, on table) 
        """
        for sub, objs in self.graph.adjacency():
            for obj, props in objs.items():
                for prop in props:
                    if prop == handle_verb:
                        for subj1, objs1 in self.graph.adjacency():
                            if subj1 == obj:
                                for obj2, props1 in objs1.items():
                                    for prop1 in props1:
                                        if prop1 in relations:
                                            yield (sub, prop, obj, prop1, obj2)

    def has_connection(node1, node2):
        return self.graph.has_edge(node1, node2)

    def save_file(self, path):
        """ Save file at <path> location. 

        Parameters:
        -----------
        path: string
            path to save the file
        """
        logger.info('Saving file: {}'.format(path))
        with open(path, 'w') as fout:
            fout.write(self.graph)
#End of PDDLFile class
