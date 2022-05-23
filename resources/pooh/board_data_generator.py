from xml.dom import minidom
import sys


def find_by_label(nodes, label):
    return [n for n in filter_relevant(nodes) if n.attributes['inkscape:label'].value == label]

def filter_relevant(nodes):
    def _filter(node):
        if node.nodeType != node.ELEMENT_NODE:
            return False
        return node.hasAttribute('inkscape:label')
    return filter(_filter, nodes)

def get_label(node):
    if not filter_relevant([node]):
        return ""
    return node.attributes['inkscape:label'].value

def handle_region(region, region_type, label):
    print(f"Handling '{label}' which is a '{region_type}'", file=sys.stderr)

def main():
    with open("100akerwoods.svg", "r") as f:
        doc = minidom.parse(f)

    regions = find_by_label(doc.getElementsByTagName('g'), 'Regions')[0]
    features = find_by_label(doc.getElementsByTagName('g'), 'Features')[0]
    grid = find_by_label(doc.getElementsByTagName('g'), 'Grid')[0]
    background = find_by_label(doc.getElementsByTagName('g'), 'Background')[0]

    region_types = ['house', 'protected-house', 'meadow', 'wood', 'sink']
    for region_type in region_types:
        region_group = find_by_label(regions.getElementsByTagName('g'), region_type)[0]
        for region in filter_relevant(region_group.childNodes):
            label = get_label(region)
            if region.tagName == "g":
                print(f"{label} skipped for now because it's a group", file=sys.stderr)
                continue
            if region.tagName != "path":
                print(f"{label} was unexpectedly a {region.tagName}!", file=sys.stderr)
                continue
            handle_region(region, region_type, label)


if __name__ == "__main__":
    main()
