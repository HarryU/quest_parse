import pytest
from bs4 import BeautifulSoup
from collections import defaultdict


@pytest.fixture
def quest_table():
    return "<table class=\"questreq\"><ul><li><a>Thing</a></li><li><a>Other</a></li><li><a>Another<ul><li><a>More</a></li></ul></a></li><li><a>Last</a></li></ul></table>"


@pytest.fixture
def input_html():
    return "<html><table class=\"this\"><tbody></tbody></table><table class=\"questreq\"><ul><li><a>Thing</a></li><li><a>Other</a></li><li><a>Another<ul><li><a>More</a></li></ul></a></li><li><a>Last</a></li></ul></table></html>"


def test_gets_table_by_class(input_html, quest_table):
    assert str(get_table(input_html, 'questreq')) == quest_table


def test_gets_differet_table_by_class(input_html):
    other_table = "<table class=\"this\"><tbody></tbody></table>"
    assert str(get_table(input_html, 'this')) == other_table


def test_only_gives_a_table(quest_table):
    input_html = "<html><p class=\"questreq\"></p><table class=\"questreq\"><ul><li><a>Thing</a></li><li><a>Other</a></li><li><a>Another<ul><li><a>More</a></li></ul></a></li><li><a>Last</a></li></ul></table></html>"
    assert str(get_table(input_html, 'questreq')) == quest_table


def test_gets_table_list_items():
    table = "<table class=\"questreq\"><ul><li><a>Thing</a></li></ul></table>"
    table = BeautifulSoup(table, 'html.parser').ul
    assert get_list_items(table) == {"Thing": []}


def test_correctly_parses_nested_list():
    table = "<table class=\"questreq\"><tbody><tr><th>junk</th></tr><tr><td><ul><li>outer<ul><li><a>content</a></li><li><a>other</a></li></ul></li></ul></td></tr></tbody></table>"
    table = BeautifulSoup(table, 'html.parser').ul
    assert get_list_items(table) == {"outer": ["content", "other"]}


def test_correctly_parses_nested_attribute_list():
    table = "<table class=\"questreq\"><tbody><tr><th>junk</th></tr><tr><td><ul><li><a>outer</a><ul><li><a>content</a></li><li><a>other</a></li></ul></li></ul></td></tr></tbody></table>"
    table = BeautifulSoup(table, 'html.parser').ul
    assert get_list_items(table) == {"outer": ["content", "other"]}


@pytest.mark.skip
def test_gets_text_split_by_attribute_tags():
    table = "<table class=\"questreq\"><tbody><tr><th>junk</th></tr><tr><td><ul><li><a>outer</a><ul><li>extra <a>content</a></li><li><a>other</a></li></ul></li></ul></td></tr></tbody></table>"
    table = BeautifulSoup(table, 'html.parser').ul
    assert get_list_items(table) == {"outer": ["extra content", "other"]}


def test_handles_double_nested_lists():
    table = "<ul><li>outer<ul><li>first child</li><li>nested parent<ul><li>second child</li></ul></li></ul></li></ul>"
    table = BeautifulSoup(table, 'html.parser').ul
    assert get_list_items(table) == {"outer": ["first child", "nested parent"]}


def test_simplify_dict_simple():
    input_dict = {1: {}, 2: {}}
    assert simplify_dict(input_dict) == {1: [], 2: []}


def test_simplify_dict_one_level():
    input_dict = {1: {2: {}}, 3: {}}
    assert simplify_dict(input_dict) == {1: [2], 2: [], 3: []}


def test_simplify_dict_complex():
    input_dict = {1: {2: {3: {}}}}
    assert simplify_dict(input_dict) == {1: [2], 2: [3], 3: []}


def test_simplify_dict_4_levels():
    input_dict = {1: {2: {3: {4: {}}}}}
    assert simplify_dict(input_dict) == {1: [2], 2: [3], 3: [4], 4: []}


def test_simplify_dict_5_levels():
    input_dict = {1: {2: {3: {4: {5: {}}}}}}
    assert simplify_dict(input_dict) == {1: [2], 2: [3], 3: [4], 4: [5], 5: []}


def test_get_all_keys_simple():
    input_dict = {1: {}}
    assert get_nested_dict_keys(input_dict) == [1]


def test_get_all_keys_one_level_of_nesting():
    input_dict = {1: {2: {}}}
    assert get_nested_dict_keys(input_dict) == [1, 2]


def simplify_dict(input_dict):
    simple_dict = defaultdict(list)
    dict_queue = [input_dict]
    while dict_queue:
        current_node = dict_queue.pop()
        for key in current_node.keys():
            simple_dict[key] = list(current_node[key])
        dict_queue.extend(list(current_node.values()))
    return dict(simple_dict)


def get_nested_dict_keys(input_dict):
    top_level_keys = input_dict.keys()
    keys = list(top_level_keys)
    for key in top_level_keys:
        if input_dict[key].keys():
            keys.extend(get_nested_dict_keys(input_dict[key]))
    return keys


def get_table(html, desired_class):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('table', class_=desired_class)


def get_list_items(table):
    list_items = {}
    for li in table.find_all("li", recursive=False):
        children_generator = (x for x in li.stripped_strings)
        key = next(children_generator)
        ul = li.find("ul")
        if ul:
            list_items[key] = [handle(next(content.stripped_strings)) for content in ul.find_all('li', recursive=False)]
        else:
            list_items[''.join(li.stripped_strings)] = []
    return list_items


def handle(string):
    if string == 'Senliten':
        return 'Senliten fully restored'
    elif string.isdigit():
        return string + ' QPs'
    return string


def get_quest_status(status_dict, quest):
    if quest in status_dict.keys():
        return status_dict[quest] == 'COMPLETED'
    elif re.sub('^The ', '', quest) in status_dict.keys():
        return status_dict[re.sub('^The ', '', quest)] == 'COMPLETED'
    else:
        return False


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import networkx as nx
    from urllib import request
    import requests
    import requests_cache
    import json
    import re
    import time

    requests_cache.install_cache('test_cache')
    username = "tenujin"
    url = "https://apps.runescape.com/runemetrics/quests?user="+username
    response = request.urlopen(url)
    data = json.loads(response.read())

    G = nx.DiGraph()

    quests = {}
    quest_statuses = {}
    for quest in data['quests']:
        quest_statuses[quest['title']] = quest['status']
        quest_name = quest['title']
        formatted_quest_name = '_'.join(quest_name.split())
        url = "https://runescape.wiki/w/" + formatted_quest_name + '?redirect=yes'
        print(url)
        try:
            t0 = time.time()
            html = requests.get(url, headers={'User-Agent': "Magic Browser"}, allow_redirects=True).content
            t1 = time.time()
            print('http request took ', t1 - t0, 's')
            table = get_table(html, 'questreq')
            if table:
                quests.update(get_list_items(table.ul))
            else:
                quests[quest_name] = []
        except Exception as e:
            print(e)

    for quest, requirements in quests.items():
        for requirement in requirements:
            G.add_edge(quest, requirement)
    G = G.reverse()
    colours = ['g' if get_quest_status(quest_statuses, quest) else 'r' for quest in G.nodes]
    plt.figure(1, figsize=(100, 100))
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    nx.draw(G, pos, with_labels=True, arrows=True, font_size=12, node_color=colours, node_size=30000, node_shape='s', alpha=0.4)
    plt.savefig('quest_graph.png')
