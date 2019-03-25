from typing import Optional, TypeVar, Generic, cast, Iterator, Callable

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
    """Double ended singly linked list."""  # it is what is

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

    def peekBack(self) -> T:
        """Peeks from the back and assumes list is not empty."""
        return cast(Node[T], self.tail).data

    def popFront(self) -> T:
        """Pops from the front and assumes list is not empty."""
        head = cast(Node[T], self.head)
        data = head.data
        self.head = head.nextNode
        return data

    def remove(self, elem: T) -> None:
        """Removes the first element that equals the given one."""
        self.removeBy(elem.__eq__)

    def removeBy(self, cmpFunc: Callable[[T], bool]) -> None:
        """Removes the first element using the comparing function that
        returns true for the element to remove.
        """

        if self.head is not None:
            if cmpFunc(self.head.data):
                self.head = self.head.nextNode
            else:
                curNode = self.head
                while curNode.nextNode is not None and not cmpFunc(curNode.nextNode.data):
                    curNode = curNode.nextNode

                if curNode.nextNode is not None:
                    curNode.nextNode = curNode.nextNode.nextNode

    def isEmpty(self) -> bool:
        return self.head is None

    def __iter__(self) -> Iterator[T]:
        return NodeIter(self.head)
