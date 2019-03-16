from typing import Optional, TypeVar, Generic, cast, Iterator

T = TypeVar('T')

class Node(Generic[T]):
    def __init__(self, nextNode: Optional['Node[T]'], data: T):
        self.nextNode = nextNode
        self.data = data

    def __iter__(self) -> Iterator[T]:
        return NodeIter(self)


class NodeIter(Generic[T]):
    def __init__(self, node: Optional[Node[T]]):
        self.curNode = node

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        if self.curNode is not None:
            data = cast(Node[T], self.curNode).data
            self.curNode = self.curNode.nextNode
            return data
        else:
            raise StopIteration

class DoubleEndedLinkedList(Generic[T]):
    """Double ended singly linked list.""" # it is what is

    def __init__(self):
        self.head: Optional[Node[T]] = None
        self.tail: Optional[Node[T]] = None

    def __pushWhenEmpty(self, data: T) -> None:
        self.head = Node(None, data)
        self.tail = self.head

    def pushBack(self, data: T) -> None:
        if self.isEmpty():
            self.__pushWhenEmpty(data)
        else:
            tail = cast(Node[T], self.tail)
            tail.nextNode = Node(None, data)
            self.tail = tail.nextNode

    def pushFront(self, data: T) -> None:
        if self.isEmpty():
            self.__pushWhenEmpty(data)
        else:
            node = Node(self.head, data)
            self.head = node

    def peekFront(self) -> T:
        """Peeks from the front and assumes list is not empty."""
        return cast(Node[T], self.head).data

    def peekBackself(self) -> T:
        """Peeks from the back and assumes list is not empty."""
        return cast(Node[T], self.tail).data

    def popFront(self) -> T:
        """Pops from the front and assumes list is not empty."""
        head = cast(Node[T], self.head)
        data = head.data
        self.head = head.nextNode
        return data

    def isEmpty(self) -> bool:
        return self.head is None

    def __iter__(self) -> Iterator[T]:
        return NodeIter(self.head)
