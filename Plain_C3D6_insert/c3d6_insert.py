import re
# 该脚本只使用于单层的c3d6网格的内聚插入
# Written by YangShengZe   Time: 2020.4.18
# 如有BUG,欢迎联系QQ：1922875732 ，如需调试找错，可以print下面的全局变量
# 全局变量
# 该脚本较为老旧，且兼容性不好，请参考new_c3d6_insert，不过作为学习每段函数的原理用非常推荐 2020.4.25
name = 'f1;f2;f3;f4;f5;f6;f7'
# 上面变量写出set的名称，例:"Set-1;Set-2" 文件中所有generate格式的element的set
set_list = name.split(';')      # set列表
file_name = 'test2.inp'          # 要插入的文件名（生成的文件为result.inp）
text = []                       # 读取文件的信息列表
set_message = []                # 初始文件中的set信息
node_dict = {}                  # 初始的节点列表
node_len = 0                    # 初始的节点列表的长度
element_dict = {}               # 单元列表（期间会经历一次修改get_message()和modify_data()下面分别print试一试）
element_len = 0                 # 初始单元列表的长度
node_appearance = {}            # 每个节点分裂的次数
new_node = {}                   # 新的节点（分裂后）的列表
cohesive_dict = {}              # 生成的内聚单元的列表
k = 0                           # 计数符号K，与生成内聚单元有关
edge_dict = {}                  # 晶界处的内聚单元列表
inter_dict = {}                 # 晶粒处的内聚单元列表


# 中间函数部分【即只是实现主要函数里的一些小功能的】
# 获取一个节点需要分裂的次数（或者可以理解为一个节点周围有几个单元，分裂次数 = 单元数量[具体实现函数见modify_data]）
def get_node_appear(element_dict, node_dict):
    global node_appearance
    node_appearance = dict.fromkeys(node_dict, 0)
    for i in element_dict:
        for j in element_dict[i]:
            node_appearance[j] += 1
    return node_appearance


# 寻找分裂后的节点的源节点
def fin_source_node(x):
    max_node = len(node_dict)
    dele_len = len(str(max_node))
    if len(x) <= dele_len:
        return x
    return str(int(x[-dele_len:]))


# 获取一个set里的所有的单元
def get_set_element(set):
    def get_set_extreme(set):
        for i in range(len(text)):
            if text[i].startswith(f'*Elset, elset={set}'):
                start = int(text[i + 1].replace(' ', '').replace('\n', '').split(',')[0])
                end = int(text[i + 1].replace(' ', '').replace('\n', '').split(',')[1])
                return [start, end]
    extrme = get_set_extreme(set)
    start = extrme[0]
    end = extrme[1]
    eigenvalue = False
    set_element_dict = {}
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


# 获取两个set单元集合里的节点的交集
def intersection(set1,set2):
    def list_insert(set_,list_):
        for i in set_:
            for j in set_[i]:
                if j not in list_:
                    list_.append(j)
    n1 = []
    n2 = []
    list_insert(set1,n1)
    list_insert(set2,n2)
    return [var for var in n1 if var in n2]


# 获取所有的晶粒(set)之间的交点，并生成列表，如[ [set-1,set-2,[1,2,3,4]],[set-1],set-3,[4,6,7,5],.... ]
def get_all_intersection(set_list):
    all = []
    for i in range(len(set_list)):
        for j in range(i+1,len(set_list)):
            a = intersection(get_set_element(set_list[i]),get_set_element(set_list[j]))
            s = [set_list[i],set_list[j],a]
            all.append(s)
    return [i for i in all if i[2].__len__() != 0]


# 主要功能函数部分【真正修改、读取文件的函数】
# 获取inp文件中的所有节点、单元的信息
def get_message():
    global node_dict
    global node_len
    global text
    ori_inp = open(file_name)
    text = ori_inp.readlines()
    # node
    value = False
    for i in text:
        if i.startswith('*Node'):
            value = True
        elif i.startswith('*Element'): break
        if value and i != '*Node\n':
            T = i.replace(' ','').replace('\n','').split(',')
            node_dict[T[0]] = T[1:]
    try: del node_dict['']
    except: pass
    node_len = len(node_dict)
    global element_dict
    global element_len
    # Element
    eigenvalue = False
    for i in text:
        if i.startswith('*Element'):
            eigenvalue = True
        elif i.startswith('*Elset') or i.startswith('*End') or i.startswith('*Nset'): break
        if eigenvalue and not i.startswith('*Element'):
            T = i.replace(' ', '').replace('\n', '').split(',')
            element_dict[T[0]] = T[1:]
    try: del element_dict['']
    except: pass
    element_len = len(element_dict)


# 获取原始的inp文件中的set的element信息
def get_set_message():
    global set_message
    set_message = []
    for i in range(len(text)):
        if text[i].startswith('*Elset, elset='):
            set_name = re.findall(r'Elset, elset=(.*?),',text[i])
            set_node = text[i+1]
            set_message.append([set_name[0],set_node])


# 将节点重新划分，并修正单元
def modify_data():
    global new_node
    global node_appearance
    get_node_appear(element_dict,node_dict)
    max_node = len(node_dict)
    for i in node_dict:
        for j in range(node_appearance[i]):
            new_node[str(j * 10**len(str(max_node)) + int(i))] = node_dict[i]
    Node_assign = dict.fromkeys(node_dict, 0)
    for i in element_dict:
        for j in range(6):
            if Node_assign[element_dict[i][j]] < node_appearance[element_dict[i][j]]:
                Newnode = str(Node_assign[element_dict[i][j]] * (10 ** (len(str(max_node)))) + int(element_dict[i][j]))
                element_dict[i][j] = Newnode
                Node_assign[fin_source_node(element_dict[i][j])] += 1


# 获取所有的存在的内聚力单元
def get_cohesive_all():
    global cohesive_dict
    global k
    k = element_len + 1
    element_sort = sorted(int(i) for i in element_dict)
    # print('element_sort:',element_sort)
    for i in element_sort:
        for j in range(i+1,element_len+1):
            l = []
            for m in element_dict[str(i)]:
                l.extend(
                    [m, n]
                    for n in element_dict[str(j)]
                    if fin_source_node(m) == fin_source_node(n)
                )

            if len(l) == 4:
               # print(l)
                cohesive_dict[str(k)] = [l[0][0],l[1][0],l[3][0],l[2][0],l[0][1],l[1][1],l[3][1],l[2][1]]
                k += 1


# 从总的内聚单元中筛选晶界/晶粒的内聚单元
def identify_interface(set_list):
    global node_l
    node_l = get_all_intersection(set_list)
    global edge_dict
    global inter_dict
    for i in node_l:
        for j in cohesive_dict:
            s = 0
            for m in cohesive_dict[j]:
                if fin_source_node(m) in i[2]:
                    s += 1
                if s == 8:
                    edge_dict[j] = cohesive_dict[j]
    for i in cohesive_dict:
        if i not in edge_dict:
            inter_dict[i] = cohesive_dict[i]


# 执行命令,可以在不同命令下print数据进行调试
get_message()
# 例： print(node_dict)
get_set_message()
modify_data()
get_cohesive_all()
identify_interface(set_list)


# 书写数据
file = open('result.inp','w')
for i in range(len(text)):
    file.write(text[i])
    if text[i].startswith('*Node'):
        break
n_node_sort = sorted([int(i) for i in new_node.keys()])
for i in n_node_sort:
    file.write(str(i))
    file.write(',    ')
    file.write(new_node[str(i)][0])
    file.write(',    ')
    file.write(new_node[str(i)][1])
    file.write(',    ')
    file.write(new_node[str(i)][2])
    file.write('\n')

file.write('*Element, type=C3D6\n')
n_element_sort = sorted([int(i) for i in element_dict.keys()])
for i in n_element_sort:
    file.write(str(i))
    file.write(',    ')
    file.write(element_dict[str(i)][0])
    file.write(',    ')
    file.write(element_dict[str(i)][1])
    file.write(',    ')
    file.write(element_dict[str(i)][2])
    file.write(',    ')
    file.write(element_dict[str(i)][3])
    file.write(',    ')
    file.write(element_dict[str(i)][4])
    file.write(',    ')
    file.write(element_dict[str(i)][5])
    file.write('\n')

file.write('*Element, type=COH3D8\n')
cohesive_sort = sorted([int(i) for i in cohesive_dict.keys()])
for i in cohesive_sort:
    file.write(str(i))
    file.write(',    ')
    file.write(cohesive_dict[str(i)][0])
    file.write(',    ')
    file.write(cohesive_dict[str(i)][1])
    file.write(',    ')
    file.write(cohesive_dict[str(i)][2])
    file.write(',    ')
    file.write(cohesive_dict[str(i)][3])
    file.write(',    ')
    file.write(cohesive_dict[str(i)][4])
    file.write(',    ')
    file.write(cohesive_dict[str(i)][5])
    file.write(',    ')
    file.write(cohesive_dict[str(i)][6])
    file.write(',    ')
    file.write(cohesive_dict[str(i)][7])
    file.write('\n')
file.write('*Elset, elset=Elset-union, generate\n')
file.write('1,   {},   1\n'.format(element_len))
for i in set_message:
    file.write('*Elset, elset={}, generate\n'.format(i[0]))
    file.write(i[1])
file.write('*Elset, elset=Cohesive-all-set, generate\n')
file.write('{0},   {1},   1'.format(element_len+1,k-1))
file.write('\n')
file.write('*Elset, elset=Cohesive-inter-set\n')
inter_sort = sorted([int(i) for i in inter_dict.keys()])
for i in inter_sort:
    file.write(str(i))
    file.write(', \n')
file.write('*Elset, elset=Cohesive-interface-set\n')
interfance_sort = sorted([int(i) for i in edge_dict.keys()])
for i in interfance_sort:
    file.write(str(i))
    file.write(',   \n')
file.write('*End Part')


