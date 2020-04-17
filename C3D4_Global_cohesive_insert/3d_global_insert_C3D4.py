# 3d批量插入cohesive单元（全局插入）
# 该脚本暂只支持c3d4网格
# 该单元格的晶界、晶粒内插入暂时将不会开发，因为我暂时用不到，请自行开发，其实并不难。
# 全局变量
file_name = 'neper.inp'
text = []
node_dict = {}
node_len = 0
element_dict = {}
element_len = 0
node_appearance = {}
new_node = {}
cohesive_dict = {}
k = 0


# 获取文件信息，如节点、单元个数和字典
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
        else: pass
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
        elif i.startswith('*Elset') or i.startswith('*End'): break
        else: pass
        if eigenvalue:
            if i.startswith('*Element'): pass
            else:
                T = i.replace(' ', '').replace('\n', '').split(',')
                element_dict[T[0]] = T[1:]
        else: pass
    try: del element_dict['']
    except: pass
    element_len = len(element_dict)


def fin_source_node(x):
    max_node = len(node_dict)
    dele_len = len(str(max_node))
    if len(x) <= dele_len:
        return x
    if len(x) > dele_len:
        return str(int(x[-dele_len:]))


def get_node_appear(element_dict, node_dict):
    global node_appearance
    node_appearance = dict.fromkeys(node_dict, 0)
    for i in element_dict:
        for j in element_dict[i]:
            node_appearance[j] += 1
    return node_appearance


# 将节点重新划分，并修正单元
def modify_data():
    global new_node
    global node_appearance
    get_node_appear(element_dict,node_dict)
    max_node = len(node_dict)
    for i in node_dict:
        for j in range(node_appearance[i]):
            new_node[str(j * 10**len(str(max_node)) + int(i))] = node_dict[i]

    node_str_len = len(str(max_node))

    n_node_app = dict.fromkeys(new_node, 1)
    for i in element_dict:
        for j in range(4):
            for k in n_node_app:
                if n_node_app[k] != 0 and fin_source_node(k) == element_dict[i][j]:
                    element_dict[i][j] =k
                    n_node_app[k] = 0


def get_cohesive_all():
    global cohesive_dict
    global k
    k = element_len + 1
    element_sort = sorted(int(i) for i in element_dict)
    for i in element_sort:
        for j in range(i+1,element_len+1):
            l = []
            for m in element_dict[str(i)]:
                for n in element_dict[str(j)]:
                    if fin_source_node(m) == fin_source_node(n):
                        l.append([m,n])
            if len(l) == 3:
                cohesive_dict[str(k)] = [l[0][0],l[1][0],l[2][0],l[0][1],l[1][1],l[2][1]]
                k += 1


get_message()
modify_data()
get_cohesive_all()

print(node_dict)
print(node_len)
print(element_dict)
print(element_len)
print(new_node)
print(node_appearance)
print(element_dict)
print(cohesive_dict)
print(k)


# 开始书写文件
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

file.write('*Element, type=C3D4\n')
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
    file.write('\n')

file.write('*Element, type=COH3D6\n')
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
    file.write('\n')
file.write('*Elset, elset=Elset-union, generate\n')
file.write('1,   {},   1\n'.format(element_len))
file.write('*Elset, elset=Cohesive-all-set, generate\n')
file.write('{0},   {1},   1'.format(element_len+1,k-1))
file.write('\n')
file.write('*End Part')

