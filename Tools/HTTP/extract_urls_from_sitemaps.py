import xml.etree.ElementTree as ET

def get_url_list():
    url_list = []

    filename = 'customer_specific/simple_stories_in_spanish_sitemap.txt'
    with open(filename, 'r', encoding='utf-8') as f:
        site_map_text = f.read()

    site_root = ET.fromstring(site_map_text)
    for child in site_root:
        if child.tag.endswith('url'):
            for url_child in child:
                if url_child.tag.endswith('loc'):
                    url = url_child.text
                    if "-english-" not in url and 'blog' not in url and 'video' not in url:
                        url_list.append(url_child.text)

    return url_list


def process():
    url_list = get_url_list()
    for url in url_list:
        print(url)


if __name__ == '__main__':
    process()
