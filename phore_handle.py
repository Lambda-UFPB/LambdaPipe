from enum import Enum


class Vertex:
    class Types(Enum):
        METAL_COMPLEX = 1
        SALT_POSITIVE = 2
        SALT_NEGATIVE = 3
        HYDROGEN_DONOR = 4
        HYDROGEN_ACCEPTOR = 5
        PI_CATION_PRO = 6
        PI_CATION_LIG = 7
        HALOGEN = 8
        PI_STACKING = 9
        HYDROPHOBIC = 10


    def __init__(self, coor_x, coor_y, coor_z, radius, ptype, resnr=None, reschain=None, restype=None, quant=None):
        self.coor_x = coor_x
        self.coor_y = coor_y
        self.coor_z = coor_z
        self.radius = radius
        self.ptype = ptype
        self.resnr = resnr
        self.reschain = reschain
        self.restype = restype
        self.quant = quant
        self.name = f'Phore_{hash(self)}'
        self.adj = set()

    
    def _add_adj(self, vertex):
        self.adj.add(vertex)


    def _del_adj(self, vertex):
        if vertex in self.adj:
            self.adj.remove(vertex)
    

    def _is_adj(self, other):
        if other in self.adj:
            return True
        else:
            return False


    def __eq__(self, other):
        if self.coor_x == other.coor_x and self.coor_y == other.coor_y and self.coor_z == other.coor_z and self.radius == other.radius and self.ptype == self.ptype:
            return True
        else:
            return False


    def __hash__(self):
        return hash((self.coor_x, self.coor_y, self.coor_z, self.radius, self.ptype))


    def __str__(self):
        adj_list = sorted(self.adj, key=lambda x: x.phore.ptype.value)
        return f'Phore (Name: {self.name}; Type: {self.ptype.name}; Radius: {self.radius}; Coordinates: {self.coor_x}, {self.coor_y}, {self.coor_z}; Chain: {self.reschain}; Residue: {self.restype} {self.resnr}; Quantity: {self.quant}), Adjacency ({[self.name for v in adj_list]})'


class Graph:
    def __init__(self):
        self.dic = dict()


    def _add_vert(self, vertex):
        self.dic[hash(vertex)] = vertex


    def _del_vert(self, vertex):
        v = hash(vertex)
        if v in self.dic:
            del self.dic[v]


    def _vert_in(self, vertex):
        return hash(vertex) in self.dic


    def _has_verts(self, vertex_list):
        result = True
        for v in vertex_list:
            result = result and self._vert_in(v)
        return result


    def _get_verts(self, vertex_list):
        return [self.dic[hash(v)] for v in vertex_list if self._vert_in(v)]


    def _get_all_verts(self):
        return self.dic.values()


    def _hash_and_vert(self, vertex, add=False):
        v = hash(vertex)
        v_in = v in self.dic
        
        if not v_in and isinstance(vertex, Vertex):
            if add:
                self._add_vert(vertex)
            return (v, vertex)
        elif v_in: # and isinstance(vertex, int):
            return (v, self.dic[v])


    def _add_adj(self, vertex1, vertex2):
        v1, vertex1 = self._hash_and_vert(vertex1, add=True)
        v2, vertex2 = self._hash_and_vert(vertex2, add=True)
        self.dic[v1]._add_adj(vertex2)
        self.dic[v2]._add_adj(vertex1)


    def _del_adj(self, vertex1, vertex2):
        v1, vertex1 = self._hash_and_vert(vertex1)
        v2, vertex2 = self._hash_and_vert(vertex2)

        if v1 in self.dic:
            self.dic[v1]._del_adj(vertex2)

        if v2 in self.dic:
            self.dic[v2]._del_adj(vertex1)


    def _are_adj(self, vertex1, vertex2):
        v1, vertex1 = self._hash_and_vert(vertex1)
        v2, vertex2 = self._hash_and_vert(vertex2)
        
        if v1 in self.dic and v2 in self.dic:
            if self.dic[v1]._is_adj(vertex2) and self.dic[v2]._is_adj(vertex1):
                return True
            else:
                return False
        else:
            return False


    def _get_adj(self, vertex):
        vertex = hash(vertex)
        if vertex in self.dic:
            return self.dic[vertex].adj
        else:
            return None


    def __str__(self):
        graph_str = '{'
        for key, value in self.dic.items():
            graph_str = '\n'.join((graph_str, f'{str(key)}: {value}'))
        return '\n'.join((graph_str, '}'))


class Vert_Collec():
    class Scores(Enum):
        BEST_DOCKING = 1
        AVERAGE_DOCKING = 2
        STD_DEV_DOCKING = 3
        OVERALL_DOCKING = 4
        MEDICINAL = 5
        ABSORPTION = 6
        DISTRIBUTION = 7
        METABOLISM = 8
        TOXICITY = 9
        OVERALL_ADMET = 10
        OVERALL = 11


    def to_hash_tuple(vertex_list):
        return tuple([hash(v) for v in vertex_list])


    def get_empty_scores():
        return {Scores.BEST_DOCKING: None, Scores.AVERAGE_DOCKING: None, Scores.STD_DEV_DOCKING: None, Scores.OVERALL_DOCKING, Scores.MEDICINAL: None, Scores.ABSORPTION: None, Scores.DISTRIBUTION: None, Scores.METABOLISM: None, Scores.TOXICITY: None, Scores.OVERALL_ADMET: None, Scores.OVERALL: None}


    def __init__(self):
        self.dic = dict()


    def _add_verts(self, vertex_list):
        self.dic[Vert_Collec.to_hash_tuple(vertex_list)] = Vert_Collec.get_empty_scores()


    def _add_hashs(self, hash_list):
        self.dic[tuple(hash_list)] = Vert_Collec.get_empty_scores()


    def _has_hashs(self, hash_list):
        return tuple(hash_list) in self.dic

    # Best_docking, average_docking, standard_deviation_docking, overall_docking, medicinal, absorption, distribution, metabolism, toxicity, overall_admet, overall
    def _upd_score(self, hash_list, score_key, score_value):
        hash_list = tuple(hash_list)
        if self._has_hashs(hash_list) and score_key in self.dic[hash_list]:
            self.dic[score_key] = score_value


    def _upd_scores(self, hash_list, key_value_dict):
        if self._has_hashs(hash_list):
            self.dic[tuple(hash_list)].update(key_value_dict)


    def _get_score(self, hash_list, score_key):
        hash_list = tuple(hash_list)
        if hash_list in self.dic and score_key in self.dic[hash_list]:
            return self.dic[score_key]
        else:
            return None


    def _combs_in_graph(self, graph):
        graph_verts = set(graph.values())
        return [c for c in self.dic.keys() if graph_verts.issuperset(c)]
