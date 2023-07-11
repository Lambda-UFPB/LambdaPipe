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

    
    def add_adj(self, vertex):
        self.adj.add(vertex)


    def del_adj(self, vertex):
        if vertex in self.adj:
            self.adj.remove(vertex)
    

    def is_adj(self, other):
        if other in self.adj:
            return True
        else:
            return False


    def shallowcopy(self):
        return type(self)(self.coor_x, self.coor_y, self.coor_z, self.radius, self.ptype, self.resnr, self.reschain, self.restype, self.quant)


    def copy(self):
        _copy = type(self)(self.coor_x, self.coor_y, self.coor_z, self.radius, self.ptype, self.resnr, self.reschain, self.restype, self.quant)
        _copy.adj = self.adj.copy()
        return _copy


    def __eq__(self, other):
        if self.coor_x == other.coor_x and self.coor_y == other.coor_y and self.coor_z == other.coor_z and self.radius == other.radius and self.ptype == self.ptype:
            return True
        else:
            return False


    def __hash__(self):
        return hash((self.coor_x, self.coor_y, self.coor_z, self.radius, self.ptype.value))


    def __str__(self):
        adj_list = sorted(self.adj, key=lambda x: x.ptype.value)
        return f'Phore (Name: {self.name}; Type: {self.ptype.name}; Radius: {self.radius}; Coordinates: {self.coor_x}, {self.coor_y}, {self.coor_z}; Chain: {self.reschain}; Residue: {self.restype} {self.resnr}; Quantity: {self.quant}, Adjacency ({[v.name for v in adj_list]}))'


class Graph:
    def __init__(self):
        self.dic = dict()


    def add_vert(self, vertex):
        self.dic[hash(vertex)] = vertex


    def del_vert(self, vertex):
        if isinstance(vertex, Vertex):
            vertex = hash(vertex)
        if vertex in self.dic:
            del self.dic[vertex]


    def vert_in(self, vertex):
        if isinstance(vertex, Vertex):
            return hash(vertex) in self.dic
        else:
            return vertex in self.dic


    def has_verts(self, vertex_list):
        for v in vertex_list:
            if not self.vert_in(v):
                return False
        return True


    def get_vert(self, vertex):
        if isinstance(vertex, Vertex):
            vertex = hash(vertex)
        return self.dic[vertex]


    def get_vertexes(self, vertex_list):
        v_list = []
        for v in vertex_list:
            if isinstance(v, Vertex) and self.vert_in(hash(v)):
                v_list.append(v)
            elif self.vert_in(v):
                v_list.append(self.dic[v])
        return v_list


    def add_adj(self, vertex1, vertex2):
        if isinstance(vertex1, Vertex):
            vertex1 = hash(vertex1)

        if isinstance(vertex2, Vertex):
            vertex2 = hash(vertex2)

        if vertex1 is not vertex2 and vertex1 in self.dic and vertex2 in self.dic:
            self.dic[vertex1].add_adj(self.dic[vertex2])
            self.dic[vertex2].add_adj(self.dic[vertex1])
            


    def del_adj(self, vertex1, vertex2):
        if isinstance(vertex1, Vertex):
            vertex1 = hash(vertex1)

        if isinstance(vertex2, Vertex):
            vertex2 = hash(vertex2)

        if vertex1 is not vertex2 and vertex1 in self.dic and vertex2 in self.dic:
            self.dic[vertex1].del_adj(self.dic[vertex2])
            self.dic[vertex2].del_adj(self.dic[vertex1])


    def are_adj(self, vertex1, vertex2):
        if isinstance(vertex1, Vertex):
            vertex1 = hash(vertex1)

        if isinstance(vertex2, Vertex):
            vertex2 = hash(vertex2)
        
        if vertex1 in self.dic and vertex2 in self.dic and self.dic[vertex1].is_adj(self.dic[vertex2]) and self.dic[vertex2].is_adj(self.dic[vertex1]):
            return True
        else:
            return False


    def get_vert_adjs(self, vertex):
        if isinstance(vertex, Vertex):
            vertex = hash(vertex)

        if vertex in self.dic:
            return self.dic[vertex].adj
        else:
            return set()


    def copy(self):
        _copy = type(self)()
        _copy.dic = self.dic.copy()
        return _copy


    def deepcopy(self):
        _copy = type(self)()
        for value in self.dic.values():
            _copy.dic[hash(value)] = value.copy()
        return _copy


    def __str__(self):
        graph_str = '{'
        for key, value in self.dic.items():
            graph_str = '\n'.join((graph_str, f'{key}: {value},'))
        return '\n'.join((graph_str[:len(graph_str) - 1], '}'))


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


    def s_to_hash_tuple(vertex_list):
        return tuple([hash(v) if isinstance(v, Vertex) else v for v in vertex_list])


    def s_get_empty_scores():
        return dict.fromkeys((Vert_Collec.Scores(1).value, Vert_Collec.Scores(2).value, Vert_Collec.Scores(3).value, Vert_Collec.Scores(4).value, Vert_Collec.Scores(5).value, Vert_Collec.Scores(6).value, Vert_Collec.Scores(7).value, Vert_Collec.Scores(8).value, Vert_Collec.Scores(9).value, Vert_Collec.Scores(10).value, Vert_Collec.Scores(11).value))


    def __init__(self):
        self.dic = dict()


    def add_hashs(self, hash_list):
        self.dic[tuple(hash_list,)] = Vert_Collec.s_get_empty_scores()


    def add_verts(self, vertex_list):
        self.dic[Vert_Collec.s_to_hash_tuple(vertex_list)] = Vert_Collec.s_get_empty_scores()


    def has_hash_list(self, hash_list):
        return tuple(hash_list,) in self.dic

    
    def has_vert_list(self, vert_list):
        return Vert_Collec.s_to_hash_tuple(vert_list) in self.dic


    def del_hashs(self, hash_list):
        if self.has_hash_list(hash_list):
            del self.dic[hash_list]


    def del_verts(self, vert_list):
        vert_list = Vert_Collec.s_to_hash_tuple(vert_list)
        if vert_list in self.dic:
            del self.dic[vert_list]


    # Best_docking, average_docking, standard_deviation_docking, overall_docking, medicinal, absorption, distribution, metabolism, toxicity, overall_admet, overall
    def upd_score(self, hash_list, score_key, score_value):
        if isinstance(score_key, Vert_Collec.Scores):
            score_key = score_key.value

        hash_list = Vert_Collec.s_to_hash_tuple(hash_list)
        if hash_list in self.dic and score_key in self.dic[hash_list]:
            self.dic[hash_list][score_key] = score_value


    def upd_scores(self, hash_list, key_value_dict):
        hash_list = Vert_Collec.s_to_hash_tuple(hash_list)
        if hash_list in self.dic:
            self.dic[hash_list].update(key_value_dict)


    def get_score(self, hash_list, score_key):
        if isinstance(score_key, Vert_Collec.Scores):
            score_key = score_key.value

        hash_list = Vert_Collec.s_to_hash_tuple(hash_list)
        if hash_list in self.dic and score_key in self.dic[hash_list]:
            return self.dic[hash_list][score_key]
        else:
            return None


    def get_scores_all(self, hash_list):
        hash_list = Vert_Collec.s_to_hash_tuple(hash_list)
        if hash_list in self.dic:
            return self.dic[hash_list]
        else:
            return None


    def get_dict_hash(self, hash_list):
        if hash_list in self.dic:
            return {hash_list: self.dic[hash_list]}
        else:
            return None


    def get_dict_vert(self, vert_list):
        vert_list = Vert_Collec.s_to_hash_tuple(vert_list)
        if vert_list in self.dic:
            return {vert_list: self.dic[vert_list]}
        else:
            return None


    def combs_in_graph(self, graph):
        graph_verts = set(graph.values())
        return [c for c in self.dic.keys() if graph_verts.issuperset(c)]


    def with_vert(self, vertex):
        if isinstance(vertex, Vertex):
            vertex = hash(vertex)
        
        v_col = Vert_Collec()
        for hash_list in self.dic.keys():
            if vertex in hash_list:
                v_col.dic[hash_list] = self.dic[hash_list]
        return v_col


    def __str__(self):
        vcol = ['{\n']
        index = 0
        for key, value in self.dic.items():
            vcol.extend(['Hash_List ( ', str(key), ' ) : Scores ( ', str(value), ' ) , \n'])
            index += 5
        vcol[index] = vcol[index][:len(vcol[index]) - 3]
        vcol.append('\n}')
        return ''.join(vcol)
