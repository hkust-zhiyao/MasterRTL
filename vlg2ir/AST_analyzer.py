import copy, sys, time, json
from DG import *


class AST_analyzer(object):
    def __init__(self, ast):
        self.__ast = ast
        self.graph = Graph()
        self.oper_label = 0
        self.const_label = 0
        self.wire_set = set()

        self.wire_dict = {}
        self.temp_dict = {}

        self.func_set = set()
        self.func_dict = {}

    def AST2Graph(self, ast):
        self.traverse_AST(ast)
        self.graph.cal_node_width()
        self.eliminate_wires(self.graph)
        self.add_parent_edge()
        

       
    def traverse_AST(self, ast):
        node_type = ast.get_type()
        if node_type == 'Function':
            self.func_set.add(ast)
            self.analyze_function()
            return
        self.add_decl_node(ast, node_type)
        self.add_assign_edge(ast, node_type)
        
        for c in ast.children():
            self.traverse_AST(c)
    
    def add_parent_edge(self):
        for name, node in self.graph.node_dict.items():
            if node.father:
                if self.graph.node_dict[node.father].type == 'Reg':
                    self.graph.add_edge(node.father, name)

    def func2graph(self, ast, input_list):
        nodetype = ast.get_type()
        if nodetype in ['Input']:
            input_list.append(str(ast.name))
        for c in ast.children():
            self.func2graph(c, input_list)

    def analyze_function(self):
        for f in self.func_set.copy():
            input_list = []
            assign_list = []
            self.func2graph(f, input_list)
            func_list = [input_list, f]
            self.func_dict[str(f.name)] = func_list
            self.func_set.remove(f)
  
    def add_decl_node(self, ast, node_type):
        if node_type == 'Decl':
            ll = len(ast.children())
            child = ast.children()[0]
            child_type = child.get_type()
            name = child.name
            width = self.get_width(child)
            self.graph.add_decl_node(name, child_type, width, None)
            if child_type == 'Wire':
                self.wire_set.add(name)
            
            if ll == 2:
                child2 = ast.children()[1]
                self.add_assign_edge(child2)

            

    def cal_width(self, ast):
        msb = int(ast.msb.value)
        lsb = int(ast.lsb.value)
        LHS = max(msb, lsb)
        RHS = min(msb, lsb)
        width = LHS - RHS + 1
        return width

    def get_width(self, ast): # -> int
        width = ast.width
        dimens = ast.dimensions
        if width:
            width = self.cal_width(width)
        else:
            width = 1
        if dimens:
            length = dimens.lengths[0]
            length = self.cal_width(length)
        else:
            length = 1
        return width*length

    def add_assign_edge(self, ast, node_type=None, sub_dict=None):
        node_type = ast.get_type()
        if sub_dict:
            if str(ast) in sub_dict.keys():
                ast = sub_dict[str(ast)]
        ### directly assign
        if node_type in ['Assign',  'NonblockingSubstitution', 'BlockingSubstitution']:
            self.add_assign(ast)
        # elif node_type == 'EventStatement':
        #     return
        elif node_type == 'Block':
            ast_tuple = ast.statements
            for ast in ast_tuple:
                self.add_assign_edge(ast)
        ### nested if statement
        elif node_type == 'IfStatement':
            cond = ast.cond
            ts = ast.true_statement
            fs = ast.false_statement
            mux_name = 'Mux' + str(self.oper_label)
            self.oper_label += 1
            cond_width = self.get_node_width(cond)
            if not cond_width:
                if cond.get_type() == 'Concat':
                    cond_width = 2
            self.graph.add_decl_node(mux_name, 'Operator', cond_width, None)
            # add mux
            # 1. if without else -> no mux
            if not fs:
                self.add_assign(ts)
            elif fs.get_type() != 'NonblockingSubstitution':
                self.assign(cond, mux_name)
                LHS1 = self.add_assign(ts, mux_name)
                self.graph.add_edge(LHS1, mux_name)

            # 2. if with else -> one mux
            elif (ts != fs) and (ts.get_type() == fs.get_type()):
                self.assign(cond, mux_name)
                LHS0 = self.add_assign(fs, mux_name)
                LHS1 = self.add_assign(ts, mux_name)
                assert LHS0 == LHS1
                self.graph.add_edge(LHS1, mux_name)


            # 3. if else if -> multiple mux
            else:
                self.add_assign_edge(fs)
        ### nested case statement
        elif node_type in ['CaseStatement', 'CasezStatement', 'CasexStatement', 'UniqueCaseStatement']:
            cond = ast.comp
            mux_name = 'Mux' + str(self.oper_label)
            self.oper_label += 1
            self.assign(cond, mux_name)
            cond_width = self.get_node_width(cond)
            if not cond_width:
                if cond.get_type() == 'Concat':
                    cond_width = 2
            self.graph.add_decl_node(mux_name, 'Operator', cond_width, None)
            caselist = ast.caselist
            for case_assign in caselist:
                self.add_case_assign(case_assign, cond_width)

    
    def add_case_assign(self, ast, width):
        child = ast.children()
        ll = len(child)
        if ll >= 2:
            cond = child[0]
            sta = ast.statement
            mux_name = 'Mux' + str(self.oper_label)
            self.oper_label += 1
            self.assign(cond, mux_name)
    
            self.graph.add_decl_node(mux_name, 'Operator', width, None)
            LHS1 = self.add_assign(sta, mux_name)
            self.graph.add_edge(LHS1, mux_name)
        elif ll == 1:
            pass
            ### TODO: event statement
        else:
            print(ll)
            print(child)
            assert False



    def get_node_width(self, ast):
        node_type = ast.get_type()
        parent_type = ast.get_parent_type()
        
        if node_type == 'Identifier':
            width = self.graph.node_dict[ast.name].width

        elif node_type == 'Pointer':
            width = 1
        elif node_type == 'Partselect':
            self.add_new_node(ast)
            width = self.graph.node_dict[ast.var.name].width
        elif node_type == 'IntConst':
            width = self.get_width_num(ast.value)
        elif node_type in ['Concat']:
            width = None
        elif parent_type == 'UnaryOperator':
            width = self.get_node_width(ast.right)
        else:
            print(node_type)
            assert False

        return width
    def add_assign(self, ast, L=None):
        node_type = ast.get_type()
        if node_type == 'IfStatement':
            self.add_assign_edge(ast)
            return
        elif node_type == 'Block':
            ast_tuple = ast.statements
            for ast in ast_tuple:
                self.add_assign_edge(ast)
            return
        elif node_type in ['CaseStatement', 'CasezStatement', 'CasexStatement', 'UniqueCaseStatement']:
            self.add_assign_edge(ast)
            return
        elif node_type == 'EventStatement':
            return
        assert node_type in ['Assign', 'NonblockingSubstitution', 'BlockingSubstitution']
        Lval = ast.left
        Rval = ast.right
        assert (Lval.get_type() == 'Lvalue') and (Rval.get_type() == 'Rvalue')
        
        if Lval.var.get_type() == 'LConcat':
            for LH in self.add_new_node(Lval.var):
                self.assign(Rval.var, LH)
        
        else:
        
            LHS = self.add_new_node(Lval.var)
            if not L:
                self.assign(Rval.var, LHS)
            else:
                self.assign(Rval.var, L)
            return LHS

            
    def add_new_node(self, ast):
        node_type = ast.get_type()
        parent_type = ast.get_parent_type()
        if node_type == 'Identifier':
            node_name = ast.name
            assert node_name in self.graph.node_dict.keys()
        elif node_type == 'Pointer':
            name = ast.var.name
            ptr = ast.ptr.value
            node_name = name + '.PTR' + ptr
            if node_name not in self.graph.node_dict.keys():
                self.graph.add_decl_node(node_name, 'Pointer', 1, name)
        elif node_type == 'Partselect':
            name = ast.var.name
            if (ast.msb.get_type() != 'IntConst' or ast.msb.get_type() != 'IntConst'):
                node_name = name
            else:
                msb = ast.msb.value
                lsb = ast.lsb.value
                width = self.cal_width(ast)
                node_name = name + '.PS' + msb + '_' + lsb
                if node_name not in self.graph.node_dict.keys():
                    self.graph.add_decl_node(node_name, 'Partselect', width, name)
        elif node_type == 'LConcat':
            node_list = ast.list
            node_name = []
            for node in node_list:
                name = self.add_new_node(node)
                node_name.append(name)
        else:
            print(node_type)
            assert False
        return node_name
    
    def unroll_syscall(self, ast):
        nodetype = ast.get_type()
        if(nodetype in ["SystemCall"]):
            ast = ast.args[0]
        return ast

    def assign(self, ast, parent_name):
        self.rt_flag = 0
        node_type = ast.get_type()
        parent_type = ast.get_parent_type()

        if parent_type == 'Constant':
            node_name = 'Constant' + str(self.const_label)
            self.const_label += 1
            width = self.get_width_num(ast.value)          
            self.graph.add_decl_node(node_name, parent_type, width)
        elif parent_type in ['Operator', 'UnaryOperator']:
            node_name = str(node_type) + str(self.oper_label)
            self.oper_label += 1
            self.graph.add_decl_node(node_name, parent_type)
        elif parent_type in ['Concat', 'Repeat']:
            node_name = str(parent_type) + str(self.oper_label)
            self.oper_label += 1
            self.graph.add_decl_node(node_name, parent_type, 0)
        elif parent_type in ['Identifier', 'Pointer', 'Partselect']: 
            node_name = self.add_new_node(ast)
            self.rt_flag = 1
        elif parent_type == 'SystemCall':
            ast = self.unroll_syscall(ast)
            self.assign(ast, parent_name)
            return
        
        elif parent_type == 'FunctionCall':
            self.func_call(ast, parent_name)
            return
        else:
            print('ERROR, future work')
            print(ast)
            print(node_type)
            print(ast.var)
            assert False
        
        self.graph.add_edge(parent_name, node_name)
        if self.rt_flag == 1:
            return
        for c in ast.children():
            self.assign(c, node_name)
    
    def func_call(self, ast, parent_name):
        node_type = ast.get_type()
        c = list(ast.children())
        func = str(c[0])
        del c[0]
        in_list = []
        for i in c:
            in_list.append(i)
        func_list = self.func_dict[func]
        input_list = func_list[0]
        assign_list = func_list[1]
        sub_dict = dict(zip(input_list, in_list))
        self.add_assign_edge(ast, node_type, sub_dict)

    def get_width_num(self, num):
        is_string = re.findall(r"[a-zA-Z]+\'*[a-z]* |'?'*", num)
        if num in ['0', '1']:
            width = 1    
        elif '\'' in num:
            width = re.findall(r"(\d+)'(\w+)", num)
            width = int(width[0][0])
        elif is_string:
            width = len(num)
        else:
            print('ERROR: New Situation!')
            print(num)
            width = 0
            print(is_string)
            assert False
        
        return width

    
    def eliminate_wires(self, g:Graph):
        print('----- Eliminating Wires in Graph -----')
        for name, node in self.graph.node_dict.items():
            if node.father in self.wire_set:
                # print(name)
                # input()
                self.wire_set.add(name)
        g_node = g.get_all_nodes2()
        interset = g_node & self.wire_set
        ll = len(interset)
        while(len(interset)!=0):
            pre_len = len(interset)
            g = self.eliminate_wire(g)
            g_node = g.get_all_nodes2()
            interset = g_node & self.wire_set
            post_len = len(interset)
            if pre_len == post_len:
                break
        if len(interset) != 0:
            # print('Warning: uneliminated wire: ', len(interset))
            for n in interset.copy():
                neighbor = self.graph.get_neighbors(n)
                if len(neighbor) == 0:
                    self.graph.remove_node(n)
                    interset.remove(n)

            # print('Final uneliminated wire: ', len(interset))
        node_dict = self.graph.node_dict.copy()
        self.graph = g
        self.graph.load_node_dict(node_dict)

    def eliminate_wire(self, g:Graph):
        node_set = g.get_all_nodes()
        for node in node_set:
            node_list = g.get_neighbors(node)
            if node in self.wire_set:
                self.wire_dict[node] = node_list
            else:
                self.temp_dict[node] = node_list
        g_new = Graph()
        for node, node_list in self.temp_dict.items():
            for n in node_list:
                if n in self.wire_dict.keys():
                    wire_assign = self.wire_dict[n]
                    for w in wire_assign:
                        if w:
                            g_new.add_edge(node, w)
                else:
                    g_new.add_edge(node, n)
        return g_new
