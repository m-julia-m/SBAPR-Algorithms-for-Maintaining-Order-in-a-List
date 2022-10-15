from email import header
from itertools import count
from random import randrange
from tkinter import N


class DoublyLinkedNode:
    def __init__(self, value, tag = 0, prev = None, next = None):
        self.tag = tag
        self.value = value
        self.prev = prev
        self.next = next
    
    def get_tag_binary_string(self):
        return "{0:b}".format(self.tag)
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) -> str:
        return "tag: " + str(self.get_tag_binary_string()) + "\tvalue: " + str(self.value)


class DoublyLinkedList:
    def __init__(self, x):
        self.head = x
        self.tail = x
    
    def insert(self, x, y):
        """Insert element y right after element x."""
        
        y.prev = x
        y.next = x.next
        x.next = y
        if y.next is not None:
            y.next.prev = y
        
        # update tail, we can never insert new head
        if y.next is None:
            self.tail = y
    
    def delete(self, x):
        if (x.prev):
            x.prev.next = x.next
        else:
            self.head = x.next

        if (x.next):
            x.next.prev = x.prev
        else:
            self.tail = x.prev
    
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        text = "\n"
        node = self.head

        while node is not None:
            text = text + str(node) + "\n"
            node = node.next
        
        return text        


class SolutionA:
    def __init__(self, x, n_at_rebuild = 2**4, t_const = 1.5):
        
        self.t_const = t_const # overflow threshold constant
        self.n = 0 # number of elements
        self.n_at_rebuild = n_at_rebuild
        self.u = self.n_at_rebuild**2 # tag universe
        self.linked_list = DoublyLinkedList(x)
    
    def insert(self, x, y):
        """Insert element y right after element x."""
        
        new_element_tag_range_min = x.tag
        new_element_tag_range_max = x.next.tag if x.next is not None else self.u

        if (new_element_tag_range_max - new_element_tag_range_min <= 1):
            # no available tag -> rebalance            
            self.rebalance_upon(x)
            new_element_tag_range_min = x.tag
            new_element_tag_range_max = x.next.tag if x.next is not None else self.u
            y.tag = randrange(new_element_tag_range_min + 1, new_element_tag_range_max)
            self.linked_list.insert(x, y)


        else:
            # use any tag from the range (excluding the bounds)
            y.tag = randrange(new_element_tag_range_min + 1, new_element_tag_range_max)
            self.linked_list.insert(x, y)

        self.n += 1


        if self.needs_rebuild:
            self.rebuild()
    
    def delete(self, x):
        self.linked_list.delete(x)

        self.n -= 1

        if (self.needs_rebuild):
            self.rebuild()
    
    def rebalance_upon(self, x):
        # find smallest enclosing range of x not in overflow

        print("rebalance upon " + str(x))

        range_identifier = x.tag # will corespond to nodes in virtual tree (trie), i.e. leftmost tag bits of all elements in subrange
        occupied_tags = 1
        level = 0 # in virtual tree, leaves are on level 0, root is on the highest level

        leftmost_element = x
        rightmost_element = x
        range_min_tag = x.tag
        range_max_tag = x.tag

        while self.density(occupied_tags, 2**level) > self.overflow_threshold(level) or level <=0:
            # while subrange is in overflow, increase range size
            range_identifier, remainder = divmod(range_identifier, 2)
            

            if (remainder == 0):
                # grow (and scan) to the right
                range_max_tag = range_max_tag + 2**level
                plus_count, rightmost_element = self.count_elements_to_right(rightmost_element, range_max_tag)
            else:
                # grow (and scna) to the left
                range_min_tag = range_min_tag - 2**level
                plus_count, leftmost_element = self.count_elements_to_left(leftmost_element, range_min_tag)
            
            occupied_tags += plus_count
            level += 1
        
        # relabel
        tag_offset = (2**level) // occupied_tags
        element_to_relabel = leftmost_element
        next_tag = range_min_tag
        for i in range(0, occupied_tags):
            element_to_relabel.tag = next_tag
            element_to_relabel = element_to_relabel.next
            next_tag += tag_offset
        
        print("after rebalance: \n" + str(self))

    def count_elements_to_right(self, element_from, max_tag):
        count = 0
        while element_from.next is not None and element_from.next.tag <= max_tag:
            element_from = element_from.next
            count += 1
        return count, element_from
    
    def count_elements_to_left(self, element_from, min_tag):
        count = 0
        while element_from.prev is not None and element_from.prev.tag >= min_tag:
            element_from = element_from.prev
            count += 1
        return count, element_from

    def density(self, occupied, total):
        return occupied / total
    
    def overflow_threshold(self, level):
        """Calculate overflow threshold based on constant t and range size (2**level)"""

        if level == 0:
            return 1
        else:
            return self.t_const ** (-level)
    
    def needs_rebuild(self):
        return not (self.n_at_rebuild/2 <= self.n <= 2*self.n_at_rebuild)
    
    def rebuild(self):
        self.n_at_rebuild = self.n
        self.u = self.n_at_rebuild**2

        print("rebuilding")

        node = self.linked_list.head
        tag = 0
        tag_offset = self.u // self.n

        while node is not None:
            node.tag = tag
            node = node.next
            tag = tag + tag_offset
    
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "T: " + str(self.t_const) + " N: " + str(self.n_at_rebuild) + " n: " + str(self.n) + " u: " + str(self.u) + " list: " + str(self.linked_list)
        



def main():
    # nodes_holder = [DoublyLinkedNode("A"), DoublyLinkedNode("B"), DoublyLinkedNode("C"), DoublyLinkedNode("D"), DoublyLinkedNode("E")]
    # structure = SolutionA(nodes_holder[0], n_at_rebuild=2**3)
    # print(structure)
    # structure.insert(nodes_holder[0], nodes_holder[3])
    # print(structure)
    # structure.insert(nodes_holder[0], nodes_holder[1])
    # print(structure)
    # structure.insert(nodes_holder[1], nodes_holder[2])
    # print(structure)
    # structure.insert(nodes_holder[3], nodes_holder[4])

    # print(structure)

    nodes_holder = [DoublyLinkedNode("0")]
    structure = SolutionA(nodes_holder[0], n_at_rebuild=2**3)

    used_nodes = [nodes_holder[0]]
    nodes_holder = []

    for i in range(1,100):
        nodes_holder.append(DoublyLinkedNode("N" + str(i)))

    
    for j in range(0, len(nodes_holder)):
        node_i =  randrange(0, len(nodes_holder))
        node = nodes_holder.pop(node_i)
        used_nodes.append(node)
        structure.insert( used_nodes[j % 2], node)

        print(structure)



    

if __name__ == "__main__":
    main()