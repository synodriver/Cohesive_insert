ori_inp = open('test2.inp')
text = ori_inp.readlines()


# --以下为功能调用型函数-- #
# 该函数用来获取inp文件中每个Node，并生成dict
def extract_node(text):
    eigenvalue = False
    node_dict = {}
    for i in text:
        if i.startswith('*Node'):
            eigenvalue = True
        elif i.startswith('*Element'):
            return node_dict
        else: pass
        if eigenvalue and i != '*Node\n':
            T = i.replace(' ', '').replace('\n', '').split(',')
            node_dict[T[0]] = T[1:]
        else: pass


# 该函数用来获取inp文件中所有Element集合，并生成dict
def extract_element(text):
    eigenvalue = False
    element_dict = {}
    for i in text:
        if i.startswith('*Element'):
            eigenvalue = True
        elif i.startswith('*Nset') or i.startswith('*End'):
            return element_dict
        else: pass
        if eigenvalue:
            if i.startswith('*Element'): pass
            else:
                T = i.replace(' ', '').replace('\n', '').split(',')
                element_dict[T[0]] = T[1:]
        else: pass


# 该函数用来获取指定Set的Element的起始值和终止值
def get_set_extreme(text, set):
    for i in range(len(text)):
        if text[i].startswith('*Elset, elset={}'.format(set)):
            start = int(text[i+1].replace(' ','').replace('\n','').split(',')[0])
            end = int(text[i+1].replace(' ','').replace('\n','').split(',')[1])
            return [start,end]
        else: pass


# 该函数用来获取指定Set的所有Element集合，并生成dict
def get_set_element(text,set):
    eigenvalue = False
    set_element_dict = {}
    start = get_set_extreme(text, set)[0]
    end = get_set_extreme(text, set)[1]
    for i in text:
        if i.startswith('*Element'):
            eigenvalue = True
        elif i.startswith('*Nset'):
            return set_element_dict
        else: pass
        if eigenvalue:
            if i.startswith('*Element'): pass
            else:
                T = i.replace(' ', '').replace('\n', '').split(',')
                if int(T[0]) in range(start,end+1):
                    set_element_dict[T[0]] = T[1:]
        else: pass


# 该函数用来获取任意两个set的点集和交接处的点集，[0]或[1]是set内，[2]是交界处,[3]和[4]是set们除去边界的点
def get_pair_set_node(set1,set2):
    s1 = []
    s2 = []
    for i in set1:
        for j in set1[i]:
            if j not in s1:
                s1.append(j)
    for i in set2:
        for j in set2[i]:
           if j not in s2:
               s2.append(j)
    edge = [var for var in s1 if var in s2]
    s1_q_edge = [var for var in s1 if var not in edge]
    s2_q_edge = [var for var in s2 if var not in edge]
    return [s1,s2,edge,s1_q_edge,s2_q_edge]


# 该函数获取全局的所有node周围的单元数，以字典形式表示
def get_node_appear(element_dict,node_dict):
    node_appearance = dict.fromkeys(node_dict,0)
    for i in element_dict:
        for j in element_dict[i]:
            node_appearance[j] += 1
    return node_appearance


# 该函数生成新的node节点，方便后面插入内聚单元
def generate_node(element_dict,node_dict):
    new_node = {}
    node_appearance = get_node_appear(element_dict,node_dict)
    max_node = len(node_dict)
    for i in node_dict:
        for j in range(node_appearance[i]+1):
            new_node[str(j * 10**len(str(max_node)) + int(i))] = node_dict[i]
    return new_node


# 此函数用来寻找原node节点
def fin_source_node(x,node_dict):
    max_node = len(node_dict)
    dele_len = len(str(max_node))
    if len(x) <= dele_len:
        return x
    if len(x) > dele_len:
        return str(int(x[-dele_len:]))


# 此函数用来生成修正后的单元
def modify_element(element_dict,node_dict):
    max_node = len(node_dict)
    node_len = len(str(max_node))
    new_node = generate_node(element_dict,node_dict)
    n_node_app = dict.fromkeys(new_node, 1)
    for i in element_dict:
        for j in range(3):
            for k in n_node_app:
                if n_node_app[k] != 0 and fin_source_node(k,node_dict) == element_dict[i][j]:
                    element_dict[i][j] =k
                    n_node_app[k] = 0
    return element_dict


# 该函数用来生成内聚单元;[0]是字典；[1]是计数器k
def generate_coh_element(element_dict,node_dict):
    cohesive_dict = {}
    all_element = extract_element(text)
    element_end = len(all_element)
    k = element_end +1
    element = modify_element(element_dict,node_dict)
    element_sort = sorted(int(i) for i in element.keys())
    print(element)
    print(element_sort)
    for i in element_sort:
        for j in range(i+1,element_end+1):
            l = []
            for m in element[str(i)]:
                for n in element[str(j)]:
                    if fin_source_node(m,node_dict) == fin_source_node(n,node_dict):
                        l.append([m,n])
            if len(l) == 2:
            # 顺序排错会造成单元过渡扭曲从而报错。
                cohesive_dict[str(k)] = [l[1][0],l[0][0],l[0][1],l[1][1]]
                k += 1
    print(k)
    print(cohesive_dict)
    return [cohesive_dict,k]


# --以下为实现函数-- #
# 书写新的点集进inp文件（包括开头）
def generate_node_code(text):
    all_node = extract_node(text)
    all_element = extract_element(text)
    new_node = generate_node(all_element,all_node)
    n_node_app = dict.fromkeys(new_node, 1)
    n_node_sort = sorted([int(i) for i in new_node.keys()])
    n_input = open('test_new.inp','w')
    for i in range(len(text)):
        n_input.write(text[i])
        if text[i].startswith('*Node'):
            break
    for i in n_node_sort:
        n_input.write(str(i))
        n_input.write(',    ')
        n_input.write(new_node[str(i)][0])
        n_input.write(',    ')
        n_input.write(new_node[str(i)][1])
        n_input.write('\n')


def generate_element_code(text):
    all_node = extract_node(text)
    all_element = extract_element(text)
    m_e = modify_element(all_element,all_node)
    n_me_sort = sorted([int(i) for i in m_e.keys()])
    n_input = open('test_new.inp','a')
    n_input.write('*Element, type=CPS3')
    n_input.write('\n')
    for i in n_me_sort:
        n_input.write(str(i))
        n_input.write(',    ')
        n_input.write(m_e[str(i)][0])
        n_input.write(',    ')
        n_input.write(m_e[str(i)][1])
        n_input.write(',    ')
        n_input.write(m_e[str(i)][2])
        n_input.write('\n')


def generate_cohesive_code(text):
    all_node = extract_node(text)
    all_element = extract_element(text)
    co_element_all = generate_coh_element(all_element,all_node)
    co_element = co_element_all[0]
    k2 = co_element_all[1]
    element_end = len(all_element)
    end = element_end +1
    n_input = open('test_new.inp','a')
    n_input.write('*Element,type=COH2D4\n')
    for i in range(end,k2):
        n_input.write(str(i))
        n_input.write(', ')
        n_input.write(co_element[str(i)][0])
        n_input.write(', ')
        n_input.write(co_element[str(i)][1])
        n_input.write(', ')
        n_input.write(co_element[str(i)][2])
        n_input.write(', ')
        n_input.write(co_element[str(i)][3])
        n_input.write('\n')
    n_input.write('*Elset, elset=Elset-Unionset, generate\n')
    n_input.write('1,   {},   1\n'.format(end-1))
    n_input.write('*Elset, elset=cohesive-set, generate\n')
    n_input.write('{0},   {1},   1'.format(end,k2-1))
    n_input.write('\n')
    n_input.write('*End Part')


generate_node_code(text)
generate_element_code(text)
generate_cohesive_code(text)

