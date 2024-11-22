import requests
from bs4 import BeautifulSoup


def process():
    root_page = "https://docs.dynatrace.com/docs/platform/davis-ai/use-cases/davis-dql-examples"
    # root_page = "https://docs.dynatrace.com/docs/observe-and-explore/metrics/dql-examples"
    # root_page = "https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language/dql-best-practices"

    # This page has special requirements!
    # root_page = "https://docs.dynatrace.com/docs/observe-and-explore/logs/logs-on-grail-examples"
    include_after = "Example 1: Status codes and counts"
    exclude_after = 'Example 4: Create a log metric'
    include_after_found = False
    exclude_after_found = False

    r = requests.get(root_page)
    soup = BeautifulSoup(r.text, 'html.parser')

    # div_content = soup.find('div', class_="content")
    div_content = soup.find('div', class_="img-provider")

    # Iterate over all children of the "root"
    for child in div_content.descendants:
        if root_page == "https://docs.dynatrace.com/docs/observe-and-explore/logs/logs-on-grail-examples":
            if include_after in child.text:
                include_after_found = True
            else:
                if exclude_after in child.text:
                    exclude_after_found = True
            if not include_after_found or exclude_after_found:
                # print("include/exclude applies:", child)
                continue

            if str(child).startswith("<h3 "):
                print(child.text)

            if str(child).startswith("<p "):
                if "you" in child.text or "the" in child.text:
                    print(child.text)

            if "sc-445b0042-0" in str(child) and "<pre " not in str(child) and "<li " in str(child):
                for grand_child in child.descendants:
                    if str(grand_child).startswith("<li "):
                        print(grand_child.text)

            if str(child).startswith("<pre "):
                if "fetch " in child.text or "| " in child.text:
                    print(child.text)

            continue

        try:
            classy_child = child.has_attr('class')
        except AttributeError:
            classy_child = False

        if classy_child:
            # Main headers
            # if str(child).startswith('<div data-testid="table"'):
            # if 'strato-table-custom-cell-wrapper' in child['class']:
            # print("CLEAR:", child)
            # child.decompose()
            # pass
            # else:

            if "sc-a5c20416-0" in child['class']:
                print(child.text)
            else:
                # Secondary headers
                if "eYpaMr" in child['class']:
                    child_text = child.text
                    print(child_text)
                    # if "Results table" not in child_text:
                    #     print(child.text)
                else:
                    if "sc-eqUAAy" in child['class']:
                    # if "sc-fqkvVR" in child['class']:
                        print(child.text)
                    # if "sc-445b0042-0" in child['class']:
                    #     examples = child.find_all("pre", class_="sc-fqkvVR")
                    #     if examples:
                    #         for example in examples:
                    #             lines = example.find_all("span", class_="sc-eqUAAy")
                    #             for line in lines:
                    #                 print(line.text)
                # else:
                #     print(child['class'], child)

    exit(1)

    # headings = soup.find_all(header_level, class_="sc-a5c20416-0")
    # # examples = soup.find_all("pre", class_="sc-fqkvVR jjDBKl")
    # examples = soup.find_all("pre", class_="sc-fqkvVR")
    #
    # index = 0
    # for heading in headings:
    #     print(heading.text)
    #     lines = examples[index].find_all("span", class_="sc-eqUAAy")
    #     for line in lines:
    #         print(line.text)
    #
    #     print('')
    #     index += 1


if __name__ == '__main__':
    process()
