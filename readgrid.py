#! /usr/bin/env python

def read_spec(specfile):
    import json
    spec = json.loads(open(specfile).read())
    full_width = spec['width']
    full_height = spec['height']
    grids = {}
    for item in spec['grid']:
        per_cell_width = full_width / item['cols']
        per_cell_height = full_height / item['rows']
        _x = (item['col']-1) * per_cell_width
        _y = (item['row']-1) * per_cell_height
        _width = per_cell_width * item['colspan']
        _height = per_cell_height * item['rowspan']
        grids[item['file']] = {
            'x': _x,
            'y': _y,
            'width': _width,
            'height': _height
        }
    return grids

def main():
    """
    for each grid,
        each cell width = width / cols
        each cell height = height / rows
        starting location = 
            (row-1)*cellHeight
            (col-1)*cellWidth
        scaled size of video = 
            rowspan * cellHeight
            colspan * cellWidth        
    
    
    Input = grid spec
    Output = width/height and X/Y of each video
    """
    specfile = 'gridspec.json'
    print read_spec(specfile)


if __name__ == '__main__':
    main()