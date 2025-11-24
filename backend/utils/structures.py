# IMPLEMENTAÇÃO DE UMA LISTA LIGADA 
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

 
class LinkedList:
    def __init__(self):
       self.head = None
    
    # Adiciona um novo elemento no início da lista
    def add(self, data):
        node = Node(data)
        node.next = self.head
        self.head = node

    # Converte a lista ligada em uma lista Python normal
    def to_list(self):
        result = []
        current = self.head
        # Percorre toda a estrutura enquanto houver nós
        while current:
            result.append(current.data)
            current = current.next
        return result

# IMPLEMENTAÇÃO DE UMA FILA
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.items:
            return self.items.pop(0)
        return None

    def get_all(self):
        return self.items

# IMPLEMENTAÇÃO DE UMA PILHA
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.items:
            return self.items.pop()
        return None

    def get_all(self):
        return self.items

# IMPLEMENTAÇÃO DE UMA TABELA HASH
class HashTable:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key, None)
