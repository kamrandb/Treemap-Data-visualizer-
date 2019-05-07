"""Assignment 2: Trees for Treemap

=== CSC148 Winter 2019 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None

        # You will change this in Task 5
        if self._subtrees == []:
            self._expanded = False
        else:
            self._expanded = True

        # TODO: (Task 1) Complete this initializer by doing two things:
        # 1. Initialize self._colour and self.data_size, according to the
        # docstring.
        # 2. Set this tree as the parent for each of its subtrees.

        for subtree in self._subtrees:
            subtree._parent_tree = self

        if self.is_empty():
            self.data_size = 0
        elif self._subtrees == []:
            self.data_size = data_size
        else:
            self.data_size = sum([i.data_size for i in self._subtrees])

        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))

        if self.data_size == 0:
            self._colour = (0, 0, 0)

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """
        # TODO: (Task 2) Complete the body of this method.
        # Read the handout carefully to help get started identifying base cases,
        # then write the outline of a recursive step.
        #
        # Programming tip: use "tuple unpacking assignment" to easily extract
        # elements of a rectangle, as follows.
        x, y, width, height = rect
        self.rect = rect
        total_size = self.data_size
        oldx, oldy = x, y
        if width > height:
            for subtree in self._subtrees[:-1]:
                if subtree.data_size != 0:
                    wid = int(width*subtree.data_size/total_size)
                    subtree.update_rectangles((x, y, wid, height))
                    x += wid
        else:
            for subtree in self._subtrees[:-1]:
                if subtree.data_size != 0:
                    h = int(height*subtree.data_size/total_size)
                    subtree.update_rectangles((x, y, width, h))
                    y += h
        if len(self._subtrees) != 0:
            new_width = width + oldx - x
            new_height = height - y + oldy
            self._subtrees[-1].update_rectangles((x, y, new_width, new_height))

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        # TODO: (Task 2) Complete the body of this method.
        if self.is_empty() or self.data_size == 0:
            return []
        elif self._subtrees == [] or not self._expanded:
            return [(self.rect, self._colour)]
        else:
            data = []
            for sub in self._subtrees:
                data.extend(sub.get_rectangles())
            return data

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is closer to the origin.
        """
        # TODO: (Task 3) Complete the body of this method
        right_bound_1 = self.rect[2] + self.rect[0] < pos[0]
        right_bound = right_bound_1 or self.rect[3] + self.rect[1] < pos[1]

        left_bound_1 = self.rect[0] > pos[0]
        left_bound = left_bound_1 or self.rect[1] > pos[1]
        outbound = left_bound or right_bound

        if not self._expanded and not outbound:
            return self
        elif not outbound:
            for i in self._subtrees:
                x, y, wid, hei = i.rect
                leaf = len(i._subtrees) == 0
                inbound = wid+x >= pos[0] >= x and hei + y >= pos[1] >= y
                if inbound and leaf:
                    return i
                elif inbound:
                    return i.get_tree_at_position(pos)
        return None

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """
        # TODO: (Task 4) Complete the body of this method.
        if self._subtrees == []:
            return self.data_size
        else:
            self.data_size = 0
            for i in self._subtrees:
                self.data_size += i.update_data_sizes()
            return self.data_size

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        # TODO: (Task 4) Complete the body of this method.
        if self._subtrees == [] and destination._subtrees != []:
            if self._parent_tree is not None:
                self._parent_tree._subtrees.remove(self)
            destination._subtrees.append(self)
            self._parent_tree = destination

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """
        # TODO: (Task 4) Complete the body of this method
        if self._subtrees == []:
            additional_size = math.ceil(self.data_size*abs(factor))
            if factor < 0:
                if self.data_size - additional_size < 1:
                    self.data_size = 1
                else:
                    self.data_size -= additional_size
            else:
                self.data_size += additional_size
    # TODO: (Task 5) Write the methods expand, expand_all, collapse, and
    # TODO: collapse_all, and add the displayed-tree functionality to the
    # TODO: methods from Tasks 2 and 3

    def expand(self) -> None:
        """expands"""
        if self._subtrees != []:
            self._expanded = True

    def expand_all(self) -> None:
        """expands_all"""
        self.expand()
        for sub in self._subtrees:
            sub.expand_all()

    def _collapse_depth(self) -> None:
        """Just helper for collapse functions"""
        if self._subtrees != []:
            self._expanded = False
            for i in self._subtrees:
                i._collapse_depth()

    def collapse(self) -> None:
        """collapses"""
        if self._parent_tree is not None:
            self._parent_tree._collapse_depth()

    def collapse_all(self) -> None:
        """collapses all"""
        if self._parent_tree is None:
            self._collapse_depth()
        else:
            self._parent_tree.collapse_all()

    # Methods for the string representation
    def get_path_string(self, final_node: bool = True) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name. If <final_node>, then add the suffix for the tree.
        """
        if self._parent_tree is None:
            path_str = self._name
            if final_node:
                path_str += self.get_suffix()
            return path_str
        else:
            path_str = (self._parent_tree.get_path_string(False) +
                        self.get_separator() + self._name)
            if final_node or len(self._subtrees) == 0:
                path_str += self.get_suffix()
            return path_str

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        # Remember that you should recursively go through the file system
        # and create new FileSystemTree objects for each file and folder
        # encountered.
        #
        # Also remember to make good use of the superclass constructor!
        # TODO: (Task 1) Implement the initializer
        if os.path.isdir(path):
            leaves_class = []
            for i in os.listdir(path):
                leaves_class.append(FileSystemTree(os.path.join(path, i)))
            TMTree.__init__(self, os.path.basename(path), leaves_class)
        else:
            road = os.path.getsize(path)
            TMTree.__init__(self, os.path.basename(path), [], road)

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (folder)'


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
