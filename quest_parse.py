import pytest
from bs4 import BeautifulSoup


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
    assert get_list_items(table) == {"Thing": None}


def test_gets_multiple_list_items():
    table = "<table class=\"questreq\"><tbody><ul><li><a>content</a></li><li><a>other</a></li></ul></tbody></table>"
    table = BeautifulSoup(table, 'html.parser').ul
    assert get_list_items(table) == {"content": None, "other": None}


def test_correctly_parses_nested_list():
    table = "<table class=\"questreq\"><tbody><tr><th>junk</th></tr><tr><td><ul><li>outer<ul><li><a>content</a></li><li><a>other</a></li></ul></li></ul></td></tr></tbody></table>"
    table = BeautifulSoup(table, 'html.parser').ul
    assert get_list_items(table) == {"outer": {"content": None, "other": None}}


def test_correctly_parses_nested_attribute_list():
    table = "<table class=\"questreq\"><tbody><tr><th>junk</th></tr><tr><td><ul><li><a>outer</a><ul><li><a>content</a></li><li><a>other</a></li></ul></li></ul></td></tr></tbody></table>"
    table = BeautifulSoup(table, 'html.parser').ul
    assert get_list_items(table) == {"outer": {"content": None, "other": None}}


def test_gets_text_split_by_attribute_tags():
    table = "<table class=\"questreq\"><tbody><tr><th>junk</th></tr><tr><td><ul><li><a>outer</a><ul><li>extra<a>content</a></li><li><a>other</a></li></ul></li></ul></td></tr></tbody></table>"
    table = BeautifulSoup(table, 'html.parser').ul
    assert get_list_items(table) == {"outer": {"extracontent": None, "other": None}}


def get_table(html, desired_class):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('table', class_=desired_class)


def get_list_items(table):
    list_items = {}
    for li in table.find_all("li", recursive=False):
        key = next(li.stripped_strings)
        ul = li.find("ul")
        if ul:
            list_items[key] = get_list_items(ul)
        else:
            list_items[' '.join(li.stripped_strings)] = None
    return list_items


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
    from collections import Mapping
    from urllib import request
    import requests
    import json
    import re

    username = "tenujin"
    url = "https://apps.runescape.com/runemetrics/quests?user="+username
    response = request.urlopen(url)
    data = json.loads(response.read())

    def dict_merge(a, b, path=None):
        if path is None:
            path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    dict_merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass
                else:
                    raise Exception('conflict at ' + '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    quests = {}
    quest_statuses = {}
    for quest in data['quests']:
        quest_statuses[quest['title']] = quest['status']
        quest_name = quest['title']
        formatted_quest_name = '_'.join(quest_name.split())
        url = "https://runescape.wiki/w/" + formatted_quest_name + '?redirect=yes'
        print(url)
        try:
            html = requests.get(url, headers={'User-Agent': "Magic Browser"}, allow_redirects=True).content
            table = get_table(html, 'questreq')
            if table:
                quests = dict_merge(quests, get_list_items(table.ul))
        except Exception as e:
            print(e)
            assert False

    G = nx.DiGraph()
    quest_queue = list(quests.items())
    while quest_queue:
        v, d = quest_queue.pop()
        for nv, nd in d.items():
            G.add_edge(v, nv)
            if isinstance(nd, Mapping):
                quest_queue.append((nv, nd))
    G = G.reverse()
    colours = ['g' if get_quest_status(quest_statuses, quest) else 'r' for quest in G.nodes]
    plt.figure(1, figsize=(50, 50))
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    nx.draw(G, pos, with_labels=True, arrows=True, font_size=8, node_color=colours, node_size=1500, node_shape='s', alpha=0.4)
    plt.show()
