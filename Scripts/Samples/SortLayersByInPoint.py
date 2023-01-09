# Sort Layers by In Point.jsx
#
# This script reorders layers in the active comp, sorted by inPoint.

import AEPython as ae

scriptName = "Sort Layers by In Point"


def sortByInpoint(comp_layers: ae.LayerCollection, unlockedOnly: bool):
    total_number = comp_layers.length
    while (total_number >= 2):
        layer_was_moved = False
        for j in range(1, total_number + 1):
            # if you want to reverse the sort order, use "<" instead of ">".
            if comp_layers[j].inPoint > comp_layers[total_number].inPoint:
                if comp_layers[j].locked:
                    if unlockedOnly == False:
                        comp_layers[j].locked = False
                        comp_layers[j].moveAfter(comp_layers[total_number])
                        comp_layers[total_number].locked = True
                        layer_was_moved = True
                else:
                    comp_layers[j].moveAfter(comp_layers[total_number])
                    layer_was_moved = True
        if layer_was_moved == False:
            total_number -= 1


def SortLayersByInPoint():
    proj = ae.app.project

    # change this to True if you want to leave locked layers untouched.
    unlockedOnly = False
    if proj is not None:
        activeItem = proj.activeItem
        if activeItem is not None and isinstance(activeItem, ae.CompItem):
            ae.app.beginUndoGroup(scriptName)
            activeCompLayers = activeItem.layers
            sortByInpoint(activeCompLayers, unlockedOnly)
            ae.app.endUndoGroup()
        else:
            ae.alert("Please select an active comp to use this script", scriptName)
    else:
        ae.alert("Please open a project first to use this script.", scriptName)


SortLayersByInPoint()
