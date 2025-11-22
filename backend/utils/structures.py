# utils/structures.py

# ---------------- LISTA LIGADA ----------------
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0
    
    def add(self, value):
        new = Node(value)
        if not self.head:
            self.head = new
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new
        self.size += 1

    def to_list(self):
        arr = []
        current = self.head
        while current:
            arr.append(current.value)
            current = current.next
        return arr


# ---------------- FILA ----------------
class Queue:
    def __init__(self):
        self.items = []
    
    def enqueue(self, value):
        self.items.append(value)
        if len(self.items) > 10:  # limite de 10 pesquisas
            self.items.pop(0)
    
    def get_all(self):
        return self.items


# ---------------- PILHA ----------------
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, value):
        self.items.append(value)

    def pop(self):
        if not self.items:
            return None
        return self.items.pop()

    def get_all(self):
        return self.items


# ---------------- TABELA HASH ----------------
class HashTable:
    def __init__(self):
        self.table = {}

    def get(self, key):
        return self.table.get(key)

    def set(self, key, value):
        self.table[key] = value
