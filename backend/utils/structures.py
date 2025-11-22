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
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = new
        self.size += 1

    def to_list(self):
        arr = []
        cur = self.head
        while cur:
            arr.append(cur.value)
            cur = cur.next
        return arr


# ---------------- FILA ----------------
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, value):
        self.items.append(value)
        if len(self.items) > 10:
            self.items.pop(0)

    def get_all(self):
        return self.items


# ---------------- PILHA ----------------
class Stack:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)

    def get_all(self):
        return self.items


# ---------------- TABELA HASH ----------------
class HashTable:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
