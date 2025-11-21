class Node {
    let val: integer;
    let next: Node;
    function constructor(v: integer, n: Node) { this.val = v; this.next = n; }
    function sumFrom(): integer {
        if (this.next == undefined) {
            return this.val;
        } else {
            return this.val + this.next.sumFrom();
        }
    }
}

let head: Node = new Node(1, new Node(2, new Node(3, undefined)));
let total: integer = head.sumFrom();