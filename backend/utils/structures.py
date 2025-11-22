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
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = new
        self.size += 1

    def to_list(self):
        out = []
        cur = self.head
        while cur:
            out.append(cur.value)
            cur = cur.next
        return out


# ---------------- FILA ----------------
class Queue:
    def __init__(self, limit=10):
        self.items = []
        self.limit = limit

    def enqueue(self, value):
        self.items.append(value)
        if len(self.items) > self.limit:
            self.items.pop(0)

    def dequeue(self):
        if not self.items:
            return None
        return self.items.pop(0)

    def get_all(self):
        return list(self.items)


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

    def peek(self):
        return self.items[-1] if self.items else None

    def get_all(self):
        return list(self.items)


# ---------------- TABELA HASH (simples) ----------------
class HashTable:
    def __init__(self):
        self.table = {}

    def get(self, key):
        return self.table.get(key)

    def set(self, key, value):
        self.table[key] = value

    def delete(self, key):
        if key in self.table:
            del self.table[key]

    def to_dict(self):
        return dict(self.table)
